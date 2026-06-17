import logging
from pathlib import Path


def setup_logger(
    log_level: str = "INFO",
    log_file: Path = None,
    dev_mode: bool = False,
    console: bool = True,
) -> logging.Logger:
    if dev_mode:
        log_level = "DEBUG"

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
        fh = logging.FileHandler(log_file_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
        ))
        logger.addHandler(fh)

        if console:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG if dev_mode else logging.WARNING)
            ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
            logger.addHandler(ch)

    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("cfmanager")
