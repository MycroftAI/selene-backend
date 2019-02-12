"""Standardize logger setup.

Standardizations:
    * applications logs go into a /var/log/mycroft/<application_name>.log file
        be sure that whatever host you are logging on has the /var/log/mycroft
        directory, which is owned by the application user.
    * log files contain all log messages of all levels by default.  this can be
        very handy to debug issues with an application but won't clog up a
        console log viewer
    * log files will be rotated on a daily basis at midnight.  this makes logs
        easier to manage and use, especially when debug messages are included
    * log messages at warning level and above will be streamed to the console
        by default.  this will bring attention to any issues or potential
        issues without clogging up the console with a potentially massive
        amount of log messages.
    * log messages will be formatted as such:
        YYYY-MM-DD HH:MM:SS,FFF | LEVEL | PID | LOGGER | LOG MESSAGE

Any of the above standardizations can be overridden by changing an instance
attribute on the LoggingConfig class.  In general, this should not be done.
Possible exceptions include increasing verbosity for debugging.
"""

from os import path
from logging import (
    DEBUG,
    Formatter,
    getLogger,
    handlers,
    StreamHandler,
    WARN
)


class LoggingConfig(object):
    """Configure a logger with a daily log file and a console log"""
    def __init__(self, log_file_name):
        self.logger = getLogger()
        self.file_log_level = DEBUG
        self.console_log_level = WARN
        self.log_file_path = path.join('/var/log/mycroft', log_file_name)
        self.log_msg_formatter = Formatter(
            '{asctime} | {levelname:8} | {process:5} | {name} | {message}',
            style='{'
        )

    def _define_file_handler(self):
        """build a file handler"""
        handler = handlers.TimedRotatingFileHandler(
            filename=self.log_file_path,
            when='midnight',
            utc=True
        )
        handler.setLevel(self.file_log_level)
        handler.setFormatter(self.log_msg_formatter)

        return handler

    def _define_console_handler(self):
        """build a console, or stream, handler"""
        handler = StreamHandler()
        handler.setLevel(self.console_log_level)
        handler.setFormatter(self.log_msg_formatter)

        return handler

    def configure(self):
        """Put it all together"""
        file_handler = self._define_file_handler()
        console_handler = self._define_console_handler()
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)


def configure_logger(logger_name: str):
    """helper function that returns a logger using the base config"""
    logging_config = LoggingConfig(logger_name + '.log')
    logging_config.configure()

    return getLogger(logger_name)
