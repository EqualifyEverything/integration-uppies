# app/utils/monitoring/logger.py
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import json

# Logger Name and Level
LOGGER_NAME = "LoggyMcLogFace"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_VERBOSE = True if LOG_LEVEL == "DEBUG" else os.environ.get("LOG_VERBOSE", "False").lower() == "true"

if LOG_VERBOSE:
    FMT_STREAM = "%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s"
    datefmt = '%Y-%m-%d %H:%M:%S'
else:
    FMT_STREAM = " %(levelname)-8s %(message)s"
    datefmt = None

# Set up logger:
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOG_LEVEL)

# Create the logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Handlers
filename = f"logs/{LOGGER_NAME}-{time.strftime('%Y-%m-%d')}.log"

# Timed Rotating File Handler
timed_file_handler = TimedRotatingFileHandler(filename=filename, when="midnight", interval=1, backupCount=30)
timed_file_handler.setLevel(LOG_LEVEL)

# Size-based Rotating File Handler
size_file_handler = RotatingFileHandler(filename=filename, maxBytes=5*1024*1024, backupCount=3)  # 5MB per file
size_file_handler.setLevel(LOG_LEVEL)

shell_handler = logging.StreamHandler()
shell_handler.setLevel(LOG_LEVEL)

# Formatters
shell_formatter = logging.Formatter(FMT_STREAM, datefmt=datefmt)
json_formatter = logging.Formatter(json.dumps({
    "time": "%(asctime)s.%(msecs)03d",
    "level": "%(levelname)-8s",
    "file": "%(filename)s",
    "function": "%(funcName)s",
    "line": "%(lineno)d",
    "message": "%(message)s"
}))
size_file_handler.setFormatter(json_formatter)
timed_file_handler.setFormatter(json_formatter)
shell_handler.setFormatter(shell_formatter)

# Add handlers to logger
logger.addHandler(shell_handler)
logger.addHandler(timed_file_handler)
logger.addHandler(size_file_handler)

def configure_logger():
    """
    Reconfigure the logger.

    This function reconfigures the logger with the predefined settings.
    """
    global logger
    logger = logging.getLogger(LOGGER_NAME)

def log_exception(exc_type, exc_value, exc_traceback):
    """
    Logs an exception with its traceback.
    """
    logger.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

# Log statements for testing purposes
if __name__ == "__main__":
    import sys
    sys.excepthook = log_exception

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

