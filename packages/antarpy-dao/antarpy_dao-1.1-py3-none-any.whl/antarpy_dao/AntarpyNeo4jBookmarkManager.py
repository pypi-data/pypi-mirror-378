from neo4j import Bookmarks, Session
from threading import RLock

class AntarpyNeo4jBookmarkManager:

    def __init__(self):
        self._bookmarks = []          # list[{"id", "tag", "bookmark": Bookmarks}]
        self._lock = RLock()

    def _bm_has_values(self, bm:Bookmarks) -> bool:
        """
        Determine whether any transactions have been committed yet 

        Args:
            bm:Bookmarks: Neo4j Bookmark

        Returns:
            bool: True if Bookmar has transaction data
        """
        if not bm:
            return False
        raw = bm.raw_values() if hasattr(bm, "raw_values") else list(bm)
        return bool(raw)

    def update(self, session:Session, id:str, tag:str):
        """
        Add or update the sessions bookmarks in the list
        """        
        bm = session.last_bookmarks()
        #if not self._bm_has_values(bm):      # nothing committed yet
        #    return
        with self._lock:
            obj = next((o for o in self._bookmarks if o.get("id") == id), None)
            if obj is not None:
                obj["bookmark"] = bm
            else:
                self._bookmarks.append({"id": id, "tag": tag, "bookmark": bm})

    def get_bookmarks(self, tag:str)->Bookmarks:
        """
        Return a collation of bookmarks from this manager for a specific tag

        Args:
            tag (str): tag to search the list for

        Returns:
            Bookmarks: a collated list of Bookmarks
        """
        rtn_bookmarks = Bookmarks()
        for obj in self._bookmarks:
            if obj["tag"] == tag:
                rtn_bookmarks += obj["bookmarks"]

        return rtn_bookmarks
    
    def get_tags(self)->list:
        """
        Returns a unique list of bookmark tags that are registered 

        Returns:
            list: List of tags
        """
        tags = []
        for obj in self._bookmarks:
            if obj["tag"] not in tags:
                tags.append(obj["tag"])
        return tags
    
    def prune(self, tag:str):
        """
        Prunes the list of bookmarks for a specfied tag

        Args:
            tag (str): Tag to prune the list for
        """        
        with self._lock:
            for o in self._bookmarks[:]:
                if o["tag"] == tag:
                    self._bookmarks.remove(o)
                    
        