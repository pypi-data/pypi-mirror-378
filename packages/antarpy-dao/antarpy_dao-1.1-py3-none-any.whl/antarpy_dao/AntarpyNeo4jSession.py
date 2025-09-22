import logging
import uuid
import os
import traceback
#from ast import List
from neo4j import Session
from contextlib import contextmanager
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class AntarpyNeo4jSession:
    def __init__(self, session, access_mode, datasource, bookmark_tag = None):
        self.id = uuid.uuid4()
        self._session = session        
        self.txn = None
        self.is_in_txn = False
        self.run_stats = {}
        self.cypher = ""
        self.cypher_params = {}
        self.profile_plan = None
        self.collect_stats = False
        self.profile_cypher = False
        self.access_mode = access_mode

        self.datasource = datasource
        self.bookmark_tag = bookmark_tag

        ANTARPYDAO_STATS_ENV_VAR = os.getenv("ANTARPYDAO_STATS","").upper()
        self.ANTARPYDAO_STATS = False
        if (ANTARPYDAO_STATS_ENV_VAR and ANTARPYDAO_STATS_ENV_VAR == "TRUE"):
            self.ANTARPYDAO_STATS = True
            self.collect_stats = True
            self.profile_cypher = True

    def __enter__(self):
        # Just return self so `with ... as s:` works
        return self

    def __exit__(self, exc_type, exc, tb):        
        try:
            self.close()
        except Exception:
            raise
        # Let any exception from the with-block propagate
        return False
    
    @contextmanager
    def transaction(self, *args, **kwargs):
        self.begin(*args, **kwargs)
        try:
            yield self
        except BaseException:
            # Roll back on any error (including KeyboardInterrupt/SystemExit)
            try:
                self.rollback()
            finally:
                self.is_in_txn = False
            raise
        else:
            try:
                self.commit()
            finally:
                self.is_in_txn = False

    def get_session(self)->Session:
        return self._session

    def get_access_mode(self):
        return self.access_mode
            
    def begin(self, *args, **kwargs):
        if not self.is_in_txn:
            self.txn = self._session.begin_transaction(*args, **kwargs)
            self.is_in_txn = True
        else:
            raise RuntimeError("Transaction already open; nested transactions are not supported.")

    def commit(self):
        if self.is_in_txn:
            self.txn.commit()
            if self.bookmark_tag:
                self.datasource.bookmarks.update(self.get_session(), self.id, self.bookmark_tag)
            self.is_in_txn = False
        else:
            raise Exception("Not in Transaction.")
    
    def rollback(self):
        if self.is_in_txn:
            self.txn.rollback()
            self.is_in_txn = False
        else:
            raise Exception("Not in Transaction.")            


    def close(self):
        if self.is_in_txn: 
            formatted_stack = "".join(traceback.format_stack())
            logger.error(f'Session Close Error: Detected unresolved Transaction. Rolling back. \n\n {formatted_stack}.')
            self.rollback()
        
        # Best practise is to close your sessions for memory reasons, however a datasource.close() will perform cleanup on any open sessions.       
        if not self._session.closed():
            self._session.close()
       
        self.cypher = ""
        self.cypher_params = {}
        self.run_stats = {}
        self.profile_plan = None
        self.collect_stats = False
        self.profile_cypher = False        
        self.datasource._unregister_session(self.id)            

    def __getattr__(self, name):
        # Delegate any other attributes to the real session
        return getattr(self._session, name)
    
    def set_profile_cypher(self, status:bool):
        self.profile_cypher = status
    
    def set_collect_stats(self, status:bool):
        self.collect_stats = status
        
    def _pop_run_stats(self,runstats):
        self.run_stats = runstats
        # Log
        if self.ANTARPYDAO_STATS:
            return_stats = self._get_base_stats_dict()
            return_stats["summary"] = self.run_stats
            logger.info(return_stats)

    def _pop_cypher(self, cypher, params):
        self.cypher = cypher
        self.cypher_params = params

    def _pop_profile_stats(self, profile_plan):
        self.profile_plan = profile_plan
        # Log
        if self.ANTARPYDAO_STATS:
            return_stats = self._get_base_stats_dict()
            return_stats["profile_plan"] = self._get_profile_stats()
            logger.info(return_stats)

    def _get_base_stats_dict(self):
        return {"cypher" : self.cypher,"parameters" : self.cypher_params} 
    
    def _get_profile_stats(self):
        return_stats = {}
        if (self.profile_plan is not None):
            first_plus = self.profile_plan.find('+')
            last_plus = self.profile_plan.rfind('+')
            return_stats = self.profile_plan[first_plus:last_plus+1]
        return return_stats

    def get_query_stats(self):
        return_stats =  self._get_base_stats_dict()
        
        if (self.run_stats is not None):
            return_stats["summary"] = self.run_stats

        if (self.profile_plan is not None):
            return_stats["profile_plan"] = self._get_profile_stats()
        
        return return_stats
    
    def _chunk_list(self, data_list, chunk_size):

        """
        Generator to return chunks of the data_list of chunk_size.
        Moved from Ne4jDatasource to AntarpyNeo4jSession so that 
        calls to Generator can be isolated per session instance

        Args:
            data_list (List):   The list fo data to chunk
            chunk_size (int):   The size of each list chunk
        
        Returns:
            chunk (List):       The portion of the list
        """
        for i in range(0, len(data_list), chunk_size):
            yield data_list[i:i + chunk_size]

    # Pass through functions to the datasource added here for convenience.
    def update(self,cypher_str, params=None, format="DICT",result_xform = None, trans_size = None):
        return self.datasource._update(cypher_str,params,self,None,format,result_xform,trans_size)
    
    def query(self, cypher_str, params=None, format="DICT", result_xform = None):
        return self.datasource._query(cypher_str,params,self,None,format,result_xform)
    