import logging
from pathlib import Path

def setup_logger(log_level: str = "INFO", log_file: Path = None):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    if log_file:
        log_file_path = Path(log_file)
        try:
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            log_file_path = Path("cfmanager.log")
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        log_file_path = Path("cfmanager.log")

    logger = logging.getLogger("cfmanager")
    logger.setLevel(numeric_level)

    if not logger.handlers:
        # File handler for detailed debug logs
        fh = logging.FileHandler(log_file_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Stream handler for console warnings/errors
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

    return logger

def get_logger():
    return logging.getLogger("cfmanager")
