import logging
import os
from logging.handlers import RotatingFileHandler

def setup_antarpy_logging(
    logger_name: str = "antarpy.dao",
    *,
    # If any of these are None, they’ll be pulled from env vars
    overall_level: str | None = None,       # ANTARPYDAOLOG_LEVEL
    console_level: str | None = None,       # ANTARPYDAOLOG_CONSOLE_LEVEL
    file_level: str | None = None,          # ANTARPYDAOLOG_FILE_LEVEL
    file_path: str | None = None,           # ANTARPYDAOLOG_FILE_PATH
    use_console: bool | None = None,        # ANTARPYDAOLOG_CONSOLE=true/false
    use_file: bool | None = None,           # ANTARPYDAOLOG_FILE=true/false
    fmt: str | None = None,                 # ANTARPYDAOLOG_FORMAT
    datefmt: str | None = None,             # ANTARPYDAOLOG_DATEFMT
    propagate: bool | None = None,          # ANTARPYDAOLOG_PROPAGATE=true/false
    rotating: bool | None = None,           # ANTARPYDAOLOG_ROTATING=true/false
    max_bytes: int | None = None,           # ANTARPYDAOLOG_MAX_BYTES
    backup_count: int | None = None,        # ANTARPYDAOLOG_BACKUP_COUNT
):
    """
    Configure the 'antarpy.dao' logger (and children) with console and/or file handlers.
    Idempotent: calling this multiple times won't add duplicate handlers.
    """

    # ---------- env fallbacks ----------
    env = os.getenv
    def _tobool(v, default):
        if v is None: return default
        s = str(v).strip().lower()
        return s in {"1","true","yes","y","on"}

    def _level(name, default):
        try:
            return getattr(logging, str(name or default).upper())
        except AttributeError:
            return getattr(logging, str(default).upper())

    overall_level = _level(overall_level or env("ANTARPYDAOLOG_LEVEL", "INFO"), "INFO")
    console_level = _level(console_level or env("ANTARPYDAOLOG_CONSOLE_LEVEL", "INFO"), "INFO")
    file_level    = _level(file_level    or env("ANTARPYDAOLOG_FILE_LEVEL", "DEBUG"), "DEBUG")

    use_console = _tobool(use_console if use_console is not None else env("ANTARPYDAOLOG_CONSOLE", "true"), True)
    use_file    = _tobool(use_file    if use_file    is not None else env("ANTARPYDAOLOG_FILE", "false"), False)

    file_path   = file_path or env("ANTARPYDAOLOG_FILE_PATH")  # required only if use_file=True

    fmt      = fmt      or env("ANTARPYDAOLOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    datefmt  = datefmt  or env("ANTARPYDAOLOG_DATEFMT", "%Y-%m-%d %H:%M:%S")
    propagate = _tobool(propagate if propagate is not None else env("ANTARPYDAOLOG_PROPAGATE", "false"), False)

    rotating = _tobool(rotating if rotating is not None else env("ANTARPYDAOLOG_ROTATING", "false"), False)
    max_bytes = int(max_bytes if max_bytes is not None else env("ANTARPYDAOLOG_MAX_BYTES", "10485760"))  # 10 MB
    backup_count = int(backup_count if backup_count is not None else env("ANTARPYDAOLOG_BACKUP_COUNT", "5"))

    # ---------- logger ----------
    logger = logging.getLogger(logger_name)
    logger.setLevel(overall_level)
    logger.propagate = propagate

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # Helper to avoid duplicate handlers (same class & destination)
    def _has_equivalent_handler(target_cls, **attrs):
        for h in logger.handlers:
            if isinstance(h, target_cls):
                # For File/Rotating handlers, compare baseFilename; for console, no extra attrs
                match = True
                for k, v in attrs.items():
                    if getattr(h, k, None) != v:
                        match = False
                        break
                if match:
                    return True
        return False

    # ---------- console handler ----------
    if use_console:
        if not _has_equivalent_handler(logging.StreamHandler):
            ch = logging.StreamHandler()
            ch.setLevel(console_level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

    # ---------- file handler ----------
    if use_file:
        if not file_path:
            raise ValueError("ANTARPYDAOLOG_FILE=true but ANTARPYDAOLOG_FILE_PATH is not set.")
        if rotating:
            handler_cls = RotatingFileHandler
            eq_attrs = {"baseFilename": os.path.abspath(file_path)}
            if not _has_equivalent_handler(handler_cls, **eq_attrs):
                fh = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
                fh.setLevel(file_level)
                fh.setFormatter(formatter)
                logger.addHandler(fh)
        else:
            handler_cls = logging.FileHandler
            eq_attrs = {"baseFilename": os.path.abspath(file_path)}
            if not _has_equivalent_handler(handler_cls, **eq_attrs):
                fh = logging.FileHandler(file_path)
                fh.setLevel(file_level)
                fh.setFormatter(formatter)
                logger.addHandler(fh)

    return logger
