from ast import List
from neo4j import READ_ACCESS, WRITE_ACCESS, GraphDatabase, Bookmarks, Result
from neo4j.graph import Node, Relationship, Path
from antarpy_dao.AntarpyNeo4jSession import AntarpyNeo4jSession
from antarpy_dao.AntarpyNeo4jRetryPolicy import AntarpyNeo4jRetryPolicy
from antarpy_dao.AntarpyNeo4jBookmarkManager import AntarpyNeo4jBookmarkManager
import logging
import numbers
import pandas as pd
import json

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class AntarpyNeo4jDatasource(): 
    def __init__(self):
        self.driver = None
        self.con_details = None
        self.impersonatedUser = None
        self.active_sessions = []
        self.bookmarks = AntarpyNeo4jBookmarkManager()
    
    def _unregister_session(self, dao_session_id):
        for save_session in self.active_sessions:
            if save_session["sess"].id == dao_session_id:
                self.active_sessions.remove(save_session)

        # Manage the bookmarks - pruning tags that are no longer used
        session_tags = []
        for save_session in self.active_sessions:
            save_bookmark = save_session["save_bookmark"]
            use_bookmark = save_session["use_bookmark"]
            if save_bookmark:                
                session_tags.append(save_bookmark)
            if use_bookmark:
                session_tags.append(use_bookmark)

        # Unique set of tags
        session_tags = list(set(session_tags))
        # Get the tags used by bookmarks
        bookmark_tags = self.bookmarks.get_tags()

        # If all tag associated sessions are closed then remove from bookmark manager.
        for tag in bookmark_tags:
            if tag not in session_tags:                   
                self.bookmarks.prune(tag)

    def init_dao(self, connection_details = None ):
        self.con_details = connection_details
        self.con_details["connected"] = False
        
        if ("access_mode" not in self.con_details):
            self.con_details["access_mode"] = "WRITE"

        if (self.con_details["access_mode"] not in ("READ", "WRITE")):
            logger.warning('access_mode connection_details must be "READ" or "WRITE". Defaulting to "WRITE" ')
            self.con_details["access_mode"] = "WRITE"
         
        if ("num_retry" not in self.con_details):
            self.con_details["num_retry"] = 3
        
        if (not isinstance(self.con_details["num_retry"] , numbers.Number) ):
            logger.warning('num_retry connection_details must be a Number. Defaulting to 3 ')
            self.con_details["num_retry"] = 3
            
        if ("backoff_multiplier" not in self.con_details):
            self.con_details["backoff_multiplier"] = 0.5
        
        if (not isinstance(self.con_details["backoff_multiplier"] , numbers.Number) ):
            logger.warning('backoff_multiplier connection_details must be a Number. Defaulting to 0.5 ')
            self.con_details["backoff_multiplier"] = 0.5

        if ("batch_limit" not in self.con_details):
            self.con_details["batch_limit"] = 10000
        
        if (not isinstance(self.con_details["batch_limit"] , numbers.Number) ):
            logger.warning('batch_limit connection_details must be a Number. Defaulting to 10000 ')
            self.con_details["batch_limit"] = 10000    

        if ("trans_size" not in self.con_details):
            self.con_details["trans_size"] = 100
        
        if (not isinstance(self.con_details["trans_size"] , numbers.Number) ):
            logger.warning('trans_size connection_details must be a Number. Defaulting to 100 ')
            self.con_details["trans_size"] = 100  
 
    def connect(self):
        """connect method creates connection
        """

        if self.con_details is None:
            raise Exception("DAO driver not initialized.")
        
        if not any(k in self.con_details for k in ["con_type", "con_hostname","con_port","con_username"]):
            raise KeyError("Connection details are incomplete. Please ensure that the following keys are defined. 'con_type', 'con_hostname','con_port','con_username' and 'con_password' if applic ")
        
        con_url = self.con_details["con_type"]+"://"+self.con_details["con_hostname"]+":"+self.con_details["con_port"]
        logger.info(f'Neo4j Driver connecting to {con_url}')
        self.driver = GraphDatabase.driver(con_url, auth=(self.con_details["con_username"], self.con_details["con_password"]))
        try:
            self.driver.verify_connectivity()
            self.con_details["connected"] = True
        except Exception as e:
            logger.error(f'Error connecting to {con_url}: {e}')
            raise

    def is_connected(self):
        return self.con_details["connected"]
    
    def _check_connection(self):
        if (not self.is_connected()):
            raise Exception("Not connected to a Database Instance")

    def disconnect(self):
        self.close()

    def close(self):
        # Auto close any open sessions.
        if self.active_sessions:            
            # Clone so that the original is not affected
            for dao_session in list(self.active_sessions):                
                dao_session["sess"].close()      
        self.driver.close()
        self.driver = None
        self.con_details["connected"] = False

    def set_impersonated_user(self, uid = None):
        self.impersonatedUser = uid

    def _get_session(self, sess_database=None, access_mode=None, use_bookmark = None):

        # Throws exception if not connected.
        self._check_connection()

        if (access_mode is None):
            access_mode = self.con_details["access_mode"]

        if (access_mode not in ("READ", "WRITE")):
            raise Exception('Error: access_mode must be "READ" or "WRITE"')        

        # Default to connection database if one not provided at runtime
        if (sess_database is None):
            sess_database = self.con_details["con_database"]

        session_access_mode = READ_ACCESS \
                                if access_mode == "READ" \
                                else WRITE_ACCESS
        
        logger.info(f'Session created for database:{sess_database}, impersonated user:{self.impersonatedUser}, access_mode:{session_access_mode}')

        last_bookmarks = Bookmarks()
        if use_bookmark:
            last_bookmarks = self._bookmarks.get_bookmarks(use_bookmark)
            #for saved_session in self.active_sessions:
            #    if saved_session["save_bookmark"] == use_bookmark:
            #        last_bookmarks += saved_session["sess"]._session.last_bookmarks()

        session = self.driver.session(
                        database=sess_database, 
                        impersonated_user=self.impersonatedUser,
                        default_access_mode=session_access_mode,
                        bookmarks=last_bookmarks)
        
        return session
    
    def get_dao_session(self, database=None, access_mode=None, save_bookmark = None, use_bookmark = None):
        dao_session = AntarpyNeo4jSession(self._get_session(database,access_mode,use_bookmark), access_mode, self, save_bookmark)
        save_session = {
            "sess": dao_session,
            "save_bookmark": save_bookmark,
            "use_bookmark": use_bookmark
        }
        self.active_sessions.append(save_session)
        return dao_session

    # Convenience Object
    def get_dao_write_session(self, database=None, save_bookmark = None, use_bookmark = None):
        return self.get_dao_session(database,access_mode="WRITE", save_bookmark=save_bookmark, use_bookmark=use_bookmark)
    
    # Convenience Object
    def get_dao_read_session(self, database=None, save_bookmark = None, use_bookmark = None):
        return self.get_dao_session(database,access_mode="READ", save_bookmark=save_bookmark, use_bookmark=use_bookmark)

    # Function to copy data from the result set into a form that can be returned.
    def _consume_stats(self, result, dao_session):

        runstats = None
        profilestats = None

        if (dao_session.collect_stats or dao_session.profile_cypher):           
            summary = result.consume()

            if (dao_session.collect_stats):
                counters = summary.counters
                runstats = {
                    "result_available_after_ms": summary.result_available_after,
                    "result_consumed_after_ms": summary.result_consumed_after,
                    "contains_updates": counters.contains_updates,
                    "nodes_created": counters.nodes_created,
                    "nodes_deleted": counters.nodes_deleted,
                    "relationships_created": counters.relationships_created,
                    "relationships_deleted": counters.relationships_deleted,
                    "properties_set": counters.properties_set,
                    "labels_added": counters.labels_added,
                    "labels_removed": counters.labels_removed,
                    "indexes_added": counters.indexes_added,
                    "indexes_removed": counters.indexes_removed,
                    "constraints_added": counters.constraints_added,
                    "constraints_removed": counters.constraints_removed,
                    "system_updates": counters.system_updates,
                    "contains_system_updates": counters.contains_system_updates
                }

            if (dao_session.profile_cypher):
                profilestats = summary.profile['args']['string-representation']

        dao_session._pop_run_stats(runstats)
        dao_session._pop_profile_stats(profilestats)


    def _to_plain(self,v):
        if isinstance(v, Node):
            return {
                "element_id": v.element_id,        # or "id": v.id in older drivers
                "labels": list(v.labels),
                "properties": dict(v),             # node properties
            }
        
        if isinstance(v, Relationship):
            return {
                "element_id": v.element_id,
                "type": v.type,
                "start": v.start_node.element_id if hasattr(v, "start_node") else v.start_node,
                "end":   v.end_node.element_id   if hasattr(v, "end_node")   else v.end_node,
                "properties": dict(v),
            }
        if isinstance(v, Path):
            return {
                "nodes": [self._to_plain(n) for n in v.nodes],
                "relationships": [self._to_plain(r) for r in v.relationships],
            }
        if isinstance(v, list):
            return [self._to_plain(x) for x in v]
        if isinstance(v, dict):
            return {k: self._to_plain(x) for k, x in v.items()}
        return v  # int/str/bool/None/float etc.
        
    def as_first(self, result):
        rec = result.single()  # or result.single(strict=True) if you want an error on 0/2+ rows
        if rec is None:
            return None
        # If the record has a single field, return that value (plainified).
        if len(rec.keys()) == 1:
            return self._to_plain(rec.value())
        # Otherwise return the whole record as a dict, plainified.
        return self._to_plain(rec.data())        
    

    def _execute_with_retry(self, tx_fn, query, dao_session, format, params, result_xform):

        # Check Environment variable....as an override.
        if(dao_session.profile_cypher):
            query = "PROFILE " + query

        policy = AntarpyNeo4jRetryPolicy(retries=self.con_details["num_retry"], backoff=self.con_details["backoff_multiplier"])

        dao_session._pop_cypher(query, params)

        # Define result transformers
        def as_list(r):         return list(r)
        def as_dict(r):         return [rec.data() for rec in r]
        def as_single(r):       return self.as_first(r)
        def as_raw(r):          return r
        def as_json(r):         return json.dumps({"json": [rec.data() for rec in r]}, indent=2)
        
        def as_dataframe(r):
            try:
                import pandas as pd
            except ImportError as e:
                raise ImportError(
                    "DataFrame output requires pandas. Install with: "
                    "pip install antarpy-dao[dataframe]"
                ) from e
            return pd.DataFrame([rec.data() for rec in r])

        transformers = {
            "LIST": as_list,
            "DICT": as_dict,
            "SINGLE": as_single,
            "DATAFRAME": as_dataframe,
            "RECORD": as_raw,
            "JSON": as_json,
            "CUSTOM" : result_xform
        }

        transformer = transformers.get(format.upper(), as_list)

        # Add the old way back in to get stats.
        def generic_transaction(tx, query, session, params):
            raw_result = tx.run(query, params)
            transformed = transformer(raw_result)

            # If we're returning the raw result, don't consume  it — return directly
            if format.upper() != "RECORD":                                   
                self._consume_stats(raw_result, session)  # process stats

            return transformed        
    
        def operation():
            if dao_session.is_in_txn:            
                return generic_transaction(dao_session.txn, query, dao_session, params)
            else:
               return tx_fn(generic_transaction, query, dao_session, params)
            
        # Only apply policy for the autocommit/execute_* path don’t retry an explicit tx handle
        # Retrying the same dao_session.txn will not help and can produce a different error (e.g., “Transaction closed”), which might be classified as non-retryable.
        # Let the caller decide how to retry around a begin/commit boundary - typically with a new transaction each time 
        #if dao_session.is_in_txn:
        #    return operation()
        #else:
        #    return policy.run(operation)
    
        return policy.run(operation)
    
    
    def _validate_params(self, params):

        # ========= Inner function to validate dict keys
        def validate_dict_keys(param_dict):
            for k in param_dict:
                if not isinstance(k, str):
                    raise TypeError(f"Cypher param key '{k}' must be a string")                
                
                # Validate value
                value = param_dict[k]
                if not isinstance(value, (str, int, float, bool)):
                    raise TypeError(f"Cypher param value for key '{k}' has unsupported type: {type(value).__name__}")

        # ========= End inner function
        
        if isinstance(params, list):
            if (len(params) > 0):
                for param in params:
                    if not isinstance(param, dict):
                        raise Exception("params contents must be of type Dict") 
                    validate_dict_keys(param)

        elif isinstance(params, dict):
            validate_dict_keys(params)

        else:
            raise TypeError("params must be a dict, list or None")
            
    def _pre_check_for_dao_operation(self,params,format):
        # Make sure we have a connection
        self._check_connection()
        
        if (format.upper() not in ("LIST","DICT","RECORD","SINGLE","DATAFRAME", "JSON", "CUSTOM")):
            raise Exception('format parameter must be "LIST", "DICT" or "RECORD" ')
                                         
        # Validate params in separate function from brevity
        if params is None:
            params = {}
        else:
            self._validate_params(params)

    def _execute_dao_operation(self, cypher_str, params, dao_session, sessionTxnType, database, format, result_xform):
        # Generate a READ_ACCESS session if we dont have one - good for simple queries
        autoCloseSession = False
        if (dao_session is None):
            dao_session = self.get_dao_read_session(database) \
                    if sessionTxnType == "READ" \
                    else self.get_dao_write_session(database)
            autoCloseSession = True
            logger.debug("session created")
        else:
            logger.debug(f"session passed in {dao_session}")
            if not isinstance(dao_session, AntarpyNeo4jSession):
                raise TypeError("session must be a AntarpyNeo4jSession instance. Use either get_dao_session(), get_dao_read_session() or get_dao_write_session() to obtain one")
            if dao_session.get_session().closed():
                raise Exception(f"NEO4J Session is closed. {sessionTxnType} operation failed.")
        
        if (not dao_session.is_in_txn and format == "RECORD"):
            raise Exception('format can only be a RECORD if the session is in a transaction. Use get_dao_session and start a transaction using WITH or the begin method')

        # Check session mode vs Database mode. i.e. cant write to a read only session.
        if (sessionTxnType == "WRITE" and dao_session.get_access_mode() == "READ"):
            raise Exception('Unable to write data to a readonly connection.')
        
        try:
            result = self._execute_with_retry(dao_session.execute_read, cypher_str, dao_session, format, params,result_xform) \
                        if sessionTxnType == "READ" \
                        else self._execute_with_retry(dao_session.execute_write, cypher_str, dao_session, format, params,result_xform)
            if autoCloseSession:
                dao_session.close()

        except Exception as e:            
            try:
                if autoCloseSession:
                    dao_session.close()
            except Exception as e1:
                pass
            raise e

        return result
    
    # For expected large resultsets (> 10,000 recs) please consider  
    # * running your DAOSession in a transaction or 
    # * bypassing the DAO altogether via
        # realSession = ds.get_session()
        # real_session.run(CYPHER)
        

    #params = {"a": 1, "b": "str", "e": None}
    def _query(self, cypher_str, params=None, dao_session=None, database=None, format="DICT", result_xform = None): # bookmarks?

        self._pre_check_for_dao_operation(params, format)
        result = self._execute_dao_operation(cypher_str, params, dao_session, "READ", database, format, result_xform)
        return result

    def query(self, cypher_str, params=None, database=None, format="DICT", result_xform = None): # bookmarks?        
        return self._query(cypher_str, params=params, dao_session=None, database=database, format=format, result_xform = result_xform)
    
    # Simple key value replacement in query
    # params = {"a": 1, "b": "str", "e": None}
    # or - Batch update on a dataset of rows.
    # params = [{"a": 1, "b": "str1"},
    #           {"a": 2, "b": "str2"}
    #          ]    

    # Update method called from session passing in the session object.
    def _update(self,cypher_str, params=None, dao_session=None, database=None, format="DICT",result_xform = None, trans_size = None):
        
        if trans_size is None:
            trans_size = self.con_details["trans_size"]

        # Make sure we have a connection
        self._pre_check_for_dao_operation(params, format)

        if ("apoc.periodic.iterate" in cypher_str):
            raise Exception("Please use batch_update_APOC for apoc.periodic.iterate operations.")
                
        if params is None or isinstance(params, dict):
            result = self._execute_dao_operation(cypher_str, params, dao_session, "WRITE", database, format,result_xform)
        else:
            result = self._batch_update(cypher_str, params, dao_session, database, format, result_xform, trans_size)

        return result
    
    # Facade to _update passing in empty session object.
    # Called from datasource object.
    def update(self,cypher_str, params=None, database=None, format="DICT",result_xform = None, trans_size = None):
        return self._update(cypher_str, params=params, dao_session=None, database=database, format=format,result_xform=result_xform, trans_size=trans_size)


    """Ensure that in the notes that the operation has to be consistent with APOC conventions i.e. must contain the operations in quotes as well as the comma at the end"""
    def batch_update_APOC(self, cypher_str, database = None, data_list = None, trans_size = None, parallel = False, apoc_data_list_name = "dataList") -> List:
        """
        Batch Update routine using Neo4j apoc.periodic.iterate, a threaded update process.

        Args:
            cypher_str (String):            A apoc.periodic.iterate compatible cypher fragment. Either a fully defined statement or an update fragment accompanied by a data_list
            database(String):               The database to operate on, if None then it will be set to the default database as defined on settings
            data_list(List):                An optional List of Dicts representing the data as is the basis of the operation.
            trans_size(int):                The apoc.periodic.iterate batch size parameter. Default to 100. Number of operations per transaction.
            parallel(Boolean):              The apoc.periodic.iterate parallel parameter.  Default to False. Enables multi-threading.
            apoc_data_list_name(String):    The name of the data list where the cypher_str is fully defined (where applic)
           
        Returns:
            summary (List):                 A list of statistics dicts returned from the apoc operation.
        """
        self._check_connection()

        if trans_size is None:
            trans_size = self.con_details["trans_size"]      

        if data_list is not None:
            if not isinstance(data_list,list):
                raise Exception("data_list parameter must be of type List") 
            
            if (len(data_list) > 0):
                if not isinstance(data_list[0], dict):
                    raise Exception("data_list contents must be of type Dict") 
  
        apoc_str = cypher_str
        if "apoc.periodic.iterate" not in cypher_str:
            apoc_str = "CALL apoc.periodic.iterate(\n"

            if data_list is not None and len(data_list) > 0:
                apoc_str += f'  "UNWIND ${apoc_data_list_name} AS row RETURN row",\n'

            apoc_str += f'  {cypher_str}\n'
            apoc_str += "  {\n"

            if data_list is not None and len(data_list) > 0:
                apoc_str += f"    params: {{{apoc_data_list_name}: ${apoc_data_list_name}}},\n"

            apoc_str += f"    batchSize: {trans_size},\n"
            apoc_str += f"    parallel:  {str(parallel).lower()}\n"
            apoc_str += "  })"
            
                                
        dao_session = self.get_dao_write_session(database)
        summary = []
        if not data_list:
            result = dao_session.get_session().run(apoc_str, {})
            summary.append(result.single().data())
        else:
            # If the data list is too large - then split at self.con_details["batch_limit"]
            chunk_size = self.con_details["batch_limit"]
            if (len(data_list) > chunk_size):
                for chunk in dao_session._chunk_list(data_list, chunk_size):
                    params = {apoc_data_list_name: chunk} 
                    result = dao_session.get_session().run(apoc_str, params)
                    summary.append(result.single().data())
            else:
                params = {apoc_data_list_name: data_list}
                result = dao_session.get_session().run(apoc_str, params)
                summary.append(result.single().data())

        dao_session.close()

        return summary

    def __str__(self):
        return str(self.con_details)
    

    def batch_update_CICT(self, cypher_str, 
                          data_list:list | None = None,
                          database:str | None = None, 
                          trans_size:int | None = None, 
                          parallel = True, 
                          threads: int | None = None, 
                          on_error: str | None = None, 
                          retry_sec = 2.5) -> List:
        """
        Batch Update routine using Neo4j CALL {...} IN TRANSACTIONS syntax, a concurrent update mechanism native to Neo4j Enterprise Edition.

        Args:
            cypher_str (String):             A Cypher fragment compatible with CALL { ... } IN TRANSACTIONS. 
                                             The cypher fragment must use the row prefix when updating attributes i.e match (n:None {id=row.id}) set name = row.name
                                             Data in the data_list is : "UNWIND data_list as row"
            database (String):               Target database, or default if None.
            data_list (List):                A list of dictionaries representing batched data to process.
            trans_size (int):         Number of records per transaction. Default taken from config.
            parallel:                        Whether to run in CONCURRENT mode. 
            threads:                         Number of concurrent threads to invoke
            on_error                         "FAIL", "BREAK", "CONTINUE", "RETRY"
            retry_sec                        Number of seconds to retry
                        

        Returns:
            summary (List):                  List of results from each chunked transaction run.
        """        

        summary = []
        def get_errors(record):
            for rec in record:
                data = rec.data()
                if not data["s"]["committed"]:
                    summary.append(data)


        self._check_connection()

        if trans_size is None:
            trans_size = self.con_details["trans_size"]

        if data_list is not None:
            if not isinstance(data_list, list):
                raise Exception("data_list must be a non-empty list of dictionaries")
            if not all(isinstance(item, dict) for item in data_list):
                raise Exception("All items in data_list must be dictionaries")

        dao_session = self.get_dao_write_session(database)
           
        # Cypher must be in a quoted form and syntactically valid as an update query inside CALL { ... } IN TRANSACTIONS
        # Ensure 'WITH row' and operation are quoted (caller must provide this)

        if data_list is not None:
            cict_str = ( 
                "UNWIND $cict_data_list_name AS row\n"
                f"CALL {{\n"
                f"  WITH row\n"
                f"  {cypher_str}\n"
                f"}} IN"
            )
        else:        
            cict_str = (
                f"CALL {{\n"
                f"  {cypher_str}\n"
                f"}} IN"
            )

        # Use cases
        if not parallel:
            cict_str += " TRANSACTIONS"
        else:
            if threads:
                cict_str += f" {threads}"
            cict_str += " CONCURRENT TRANSACTIONS"

        if trans_size:
            cict_str += f" OF {trans_size} ROWS"
        
        if on_error:
            cict_str += f" ON ERROR {on_error}"
            if on_error == "RETRY":
                cict_str += f" FOR {retry_sec} SECONDS"

            if on_error in ["CONTINUE","BREAK"]:
                cict_str += "\n REPORT STATUS AS s\n RETURN s"

        #print(cict_str)
        # Split into chunks to respect batch_limit logic if needed
        chunk_size = self.con_details["batch_limit"]

        if data_list is None: 
            result = dao_session.get_session().run(cict_str)
            get_errors(result)
        else:
            for chunk in dao_session._chunk_list(data_list, chunk_size):
                #print(chunk)
                params = {"cict_data_list_name": chunk}
                result = dao_session.get_session().run(cict_str, params)
                get_errors(result)

        dao_session.close()

        return summary

    def _batch_update(self, cypher_str, data_list, dao_session=None, database=None, format="LIST", result_xform = None, trans_size = 100) -> List:

        self._check_connection()

        if not isinstance(data_list, list):
            raise TypeError("param must be a list")

        if dao_session is None:
            dao_session = self.get_dao_write_session(database)
            auto_close = True
        else:
            auto_close = False
            if not isinstance(dao_session, AntarpyNeo4jSession):
                raise TypeError("session must be a AntarpyNeo4jSession instance")

        has_error = False
        err_msg = ""
        return_list = []

        # Split Large Data Lists into chunks
        for batch_chunk in dao_session._chunk_list(data_list, self.con_details["batch_limit"]):

            # Split into trans sized chunks.
            for trans_chunk in dao_session._chunk_list(batch_chunk,trans_size):

                # Track error status - continue to exhaust Generator
                if not has_error:
                    try:
                        # Always in Transaction
                        if not dao_session.is_in_txn:
                            dao_session.begin()

                        # Process each Dict in trans_chunk list
                        for item in trans_chunk:
                            result = self._execute_dao_operation(cypher_str, item, dao_session, "WRITE", database, format, result_xform)
                            if result is not None and len(result) > 0:
                                return_list.append(result)

                        dao_session.commit()

                    except Exception as e:
                        dao_session.rollback()
                        err_msg = str(e)
                        has_error = True

        if auto_close:
            dao_session.close()

        if len(err_msg) > 0:
            raise Exception(f"Batch execution failed: {err_msg}")

        return return_list