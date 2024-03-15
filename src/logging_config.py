import logging
from decouple import config

from google.cloud import logging as cloud_logging

def start_loggers():
    "Starts loggers for error and info logs"

    environment = config("FLASK_ENV", "development") # Default to development if FLASK_ENV is not set

    error_logger = logging.getLogger("error_logger")
    info_logger = logging.getLogger("info_logger")

    if environment in ["staging", "production"]:
        # Initialize Google Cloud Logging
        logging_client = cloud_logging.Client()
        cloud_handler = logging_client.get_default_handler()

        error_logger.setLevel(logging.ERROR)
        error_logger.addHandler(cloud_handler)

        info_logger.setLevel(logging.INFO)
        info_logger.addHandler(cloud_handler)
    else:
        # Initialize local file logging
        error_log_filename = "error.log"
        info_log_filename = "info.log"

        error_handler = logging.FileHandler(error_log_filename)
        info_handler = logging.FileHandler(info_log_filename)

        error_logger.setLevel(logging.ERROR)
        error_logger.addHandler(error_handler)

        info_logger.setLevel(logging.INFO)
        info_logger.addHandler(info_handler)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        error_handler.setFormatter(formatter)
        info_handler.setFormatter(formatter)

