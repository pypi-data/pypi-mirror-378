import logging

from lsyflasksdkcore.logging.file_logger import file_logging_handler
from lsyflasksdkcore.logging.stash_logger import stash_logging_handler


def init_logging(app, logger_name: str, logger_type: str = "file"):
    if logger_type == "file":
        handler = file_logging_handler(app)
    else:
        handler = stash_logging_handler(app)

    root_logger = logging.getLogger(logger_name)
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)
