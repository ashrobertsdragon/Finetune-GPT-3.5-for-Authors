from decouple import config
from google.cloud import logging as cloud_logging

from .type_logger import TypeLogger


class LoggerManager:
    error_logger = None
    info_logger = None

    @staticmethod
    def _start_loggers():
        "Starts loggers for error and info logs"

        environment = config("FLASK_ENV", "development")

        if environment in ["staging", "production"]:
            # Initialize Google Cloud Logging
            logging_client = cloud_logging.Client()
            cloud_handler = logging_client.get_default_handler()

            error_logger = TypeLogger(name="error", handler=cloud_handler)
            info_logger = TypeLogger(name="info", handler=cloud_handler)

        else:
            # Initialize local file logging
            error_logger = TypeLogger(name="error")
            info_logger = TypeLogger(name="info")

        return error_logger, info_logger

    @staticmethod
    def initialize_loggers():
        if (
            LoggerManager.error_logger is None
            or LoggerManager.info_logger is None
        ):
            LoggerManager.error_logger, LoggerManager.info_logger = (
                LoggerManager._start_loggers()
            )

    @staticmethod
    def get_error_logger():
        return LoggerManager.error_logger

    @staticmethod
    def get_info_logger():
        return LoggerManager.info_logger


# Initialize at module load time
LoggerManager.initialize_loggers()
