# equity-aggregator/logging_config.py

import logging.config
import os
from datetime import date
from pathlib import Path

from platformdirs import user_log_dir

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": None,  # set lazily at runtime using configure_logging()
            "encoding": "utf8",
        },
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(module)-20s | %(levelname)-5s | %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "loggers": {
        "equity_aggregator": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console", "file"],
    },
}


def configure_logging(override_level: str = None) -> None:
    """
    Configures logging for the application based on override or LOG_CONFIG env variable.

    This function copies the base LOGGING configuration and adjusts console handler's
    log level according to the environment:
        - 'production': sets console log level to WARNING.
        - 'debug': sets console log level to DEBUG.
        - 'development': sets console log level to INFO.

    The file handler is always set to DEBUG level. The logger 'equity_aggregator' is set
    to DEBUG level.

    Args:
        override_level (str, optional): Override the environment log level.

    Returns:
        None
    """
    config = LOGGING.copy()

    # Resolve the log file path
    config["handlers"]["file"]["filename"] = _resolve_log_file()

    # Determine the log configuration (use override or env var, default to 'production')
    env = (override_level or os.getenv("LOG_CONFIG", "production")).lower()

    console_level = {
        "production": "WARNING",
        "debug": "DEBUG",
        "development": "INFO",
    }.get(env, "INFO")

    config["loggers"]["equity_aggregator"]["level"] = "DEBUG"

    # console handler always set to environment level
    config["handlers"]["console"]["level"] = console_level

    # file handler always set to DEBUG
    config["handlers"]["file"]["level"] = "DEBUG"

    logging.config.dictConfig(config)


def _resolve_log_file() -> str:
    """
    Resolves the log file path for the current date and ensures log directory exists.

    Checks for an override in the LOG_DIR environment variable.
    If not set, defaults to the user log directory for this application.

    Args:
        None

    Returns:
        str: Absolute path to the log file for today's date.
    """
    if log_dir_override := os.getenv("LOG_DIR"):
        log_dir = Path(log_dir_override)
    else:
        log_dir = Path(user_log_dir("equity-aggregator", "equity-aggregator"))

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"equity_aggregator_{date.today():%Y-%m-%d}.log"
    return str(log_file)
