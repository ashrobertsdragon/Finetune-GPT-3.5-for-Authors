import logging

from google.cloud import logging as cloud_logging

def start_loggers():
    "Starts loggers for error and info logs"

    logging_client = cloud_logging.Client()
    cloud_handler = logging_client.get_default_handler()

    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)
    error_logger.addHandler(cloud_handler)
    error_extra = {"labels": {"type": "error", "application": "your-application-name"}}

    info_logger = logging.getLogger("info_logger")
    info_logger.setLevel(logging.INFO)
    info_logger.addHandler(cloud_handler)
    info_extra = {"labels": {"type": "info", "application": "your-application-name"}}
