import logging
from typing import Optional, Union

from colorlog import ColoredFormatter


class LoggerConfigurator:
    def __init__(self):
        ...

    @staticmethod
    def setup_logger(
        name: Optional[str] = None,
        level: int = logging.DEBUG,
        to_console: bool = True,
        to_file: Union[str, None] = None,
    ) -> logging.Logger:
        """
        Creates a custom logger with the specified logging level, colored console formatting, and optional file logging.

        :param name: The name of the logger
        :param level: The logging level
        :param to_console: Whether to log to the console
        :param to_file: File path for logging output (if needed)
        :return: Logger instance
        """

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False

        if logger.hasHandlers():
            logger.handlers.clear()

        handlers = []

        if to_console:
            log_format = "%(log_color)s[%(asctime)s] %(levelname)s in %(module)s:%(reset)s %(message_log_color)s%(message)s"
            formatter = ColoredFormatter(
                log_format,
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red,bg_white",
                },
                secondary_log_colors={
                    "message": {
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "bold_red,bg_white",
                    }
                },
                style="%",
            )
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            handlers.append(console_handler)

        if to_file is not None:
            file_format = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            file_formatter = logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
            file_handler = logging.FileHandler(to_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)

        for handler in handlers:
            logger.addHandler(handler)

        return logger
