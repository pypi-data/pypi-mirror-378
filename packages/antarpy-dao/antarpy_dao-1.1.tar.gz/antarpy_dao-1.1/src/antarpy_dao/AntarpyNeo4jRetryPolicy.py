import time
from neo4j.exceptions import Neo4jError, TransientError, SessionExpired, ServiceUnavailable
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

_RETRYABLE_CODES = {
    "Neo.TransientError.Transaction.DeadlockDetected",
    "Neo.TransientError.Transaction.LockAcquisitionTimeout",
    "Neo.TransientError.Transaction.LockClientStopped",
}

_RETRYABLE_CODE_PREFIXES = ("Neo.TransientError", "TransientError")

class AntarpyNeo4jRetryPolicy:
    def __init__(self, retries=3, backoff=0.5, backoff_multiplier=2.0):
        self.max_retries = retries
        self.backoff = backoff
        self.backoff_multiplier = backoff_multiplier

    def _walk_causes(self, exc):
        seen = set()
        while exc and exc not in seen:
            yield exc
            seen.add(exc)
            exc = exc.__cause__ or exc.__context__

    def _is_retryable(self, exc) -> bool:
        for e in self._walk_causes(exc):
            code = getattr(e, "code", "") or ""
            # Always bail on Deadlocks
            #if not code.startswith("Neo.TransientError.Transaction.DeadlockDetected"):
            if isinstance(e, (SessionExpired, ServiceUnavailable, TransientError)):
                return True
            if isinstance(e, Neo4jError):
                if  code in _RETRYABLE_CODES or code.startswith(_RETRYABLE_CODE_PREFIXES):
                    return True
        return False        

#    def is_retryable(self, exception):
#        return isinstance(exception, (TransientError, SessionExpired, ServiceUnavailable))

    def run(self, operation, *args, **kwargs):

        delay = self.backoff
        initial_exception = None
        # N retries => N+1 attempts total
        for attempt in range(self.max_retries + 1):            
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if not initial_exception:
                    initial_exception = e

                if not self._is_retryable(e):
                    logger.error("Non-retryable exception: %s", e)                    
                    raise
                elif (attempt >= self.max_retries):
                    logger.error("Giving up after attempt %d/%d: %s",attempt + 1, self.max_retries + 1, initial_exception)
                    raise initial_exception

                logger.warning("Retryable exception on attempt %d/%d: %s; sleeping %.2fs",attempt + 1, self.max_retries + 1, e, delay)
                time.sleep(delay)
                delay *= self.backoff_multiplier

