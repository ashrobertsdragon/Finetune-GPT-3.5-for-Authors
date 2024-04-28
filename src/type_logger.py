import logging
import os

from typing import Optional
from logging import Logger, Handler, Formatter


class TypeLogger():
    """
    A class that provides a logging functionality with customizable log levels
    and log handlers.

    Attributes:
        name (str): The name of the logger.
        logger (Logger): The Logger object.
        handler (Optional[Handler]): The Handler object. Defaults to local
            FileHandler.
        formatter (Formatter): The Formatter object.
    
    Methods:
        __init__: Initializes the TypeLogger object.
            Args:
                self
                name (str): The name of the logger.
                handler (Optional[Handler]): The optional handler object.

        __call__: Calls the log method.
            Args:
                self
                message (str): The message to log.

        _get_logger: Creates a logger object.
            Args:
                self
                name (str): The name of the logger.
                
        _get_log_level: Returns the log level from the logger name.
            Args:
                self
                name (str): The name of the logger.

        _get_file_handler: Returns a local file handler object with a file
            name of the logger's name/level and .log extension.
            Args:
                self
                name (str): The name of the logger.

        _get_formatter: Returns a formatter object.

        _setup_logger: Sets up the logger, setting the level, adding the
            handler, and setting the formatter.
            Args:
                self
                name (str): The name of the logger.

        log: Logs a message using the logger.
            Args:
                self
                message (str): The message to log.

    Example:
        >>>info_logger = TypeLogger("info")
        >>>info_logger("Info logger initialized")

        >cat info.log

        Output:
        2024-04-13 23:33:39,228 - Info logger initialized
    """
    def __init__(self, *, name: str, handler: Optional[Handler] = None) -> None:
        self.name = name
        self.logger = self._get_logger(name)
        self.handler = handler if handler else self._get_file_handler(name)
        self.formatter = self._get_formatter()
        self._setup_logger(name)

    
    def __call__(self, message: str) -> None:
        self.log(message)

    def _get_logger(self, name: str) -> Logger:
        logger_name: str = f"{name}_logger"
        return logging.getLogger(logger_name)
    
    def _get_log_level(self) -> int:

        name: str = self.name.upper()
        try:
            log_level = getattr(logging, name)
        except AttributeError:
            raise ValueError(f"Invalid log level name: {name}")
        return log_level
        
    def _get_file_handler(self, name: str) -> Handler:
        filename: str = f"{name}.log"
        log_path = "logs"
        os.makedirs(log_path, exist_ok=True)

        file_path = os.path.join(log_path, filename)
        return logging.FileHandler(file_path)

    def _get_formatter(self) -> Formatter:
        return logging.Formatter(
            "%(asctime)s -%(levelname)s:%(message)s"
        )

    def _setup_logger(self, name: str) -> None:
        log_level: int = self._get_log_level()
        self.logger.setLevel(log_level)
        self.logger.addHandler(self.handler)
        self.handler.setFormatter(self.formatter)

    def log(self, message) -> None:
        """
        Log a message using the logger.

        Args:
            message (str): The message to be logged.

        Returns:
            None

        Example:
            logger = Logger("my_logger")
            logger.log("This is a log message")
        """
        self.logger.log(self.logger.level, message)



