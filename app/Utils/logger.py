import logging
import os
from logging.config import dictConfig
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Generate a timestamped log filename
log_filename = datetime.now().strftime("logs/app_%Y-%m-%d_%H-%M-%S.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "detailed": {
            "format": "[%(asctime)s] %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": log_filename,
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,  # Keep last 5 log files
            "encoding": "utf8",
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}


import logging

def setup_logger():
    logger = logging.getLogger("healthcare_app")
    logger.setLevel(logging.INFO)

    if not logger.handlers:  # Prevent adding multiple handlers
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger  # Make sure you return the logger!
