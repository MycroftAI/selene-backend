# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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
    INFO
)


class LoggingConfig(object):
    """Configure a logger with a daily log file and a console log"""
    def __init__(self, logger_name):
        """
        Initialize a logger.

        Args:
            self: (todo): write your description
            logger_name: (str): write your description
        """
        self.logger = getLogger()
        self.logger.level = DEBUG
        self.file_log_level = DEBUG
        self.console_log_level = INFO
        self.log_file_path = path.join('/var/log/mycroft', logger_name + '.log')
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
    logging_config = LoggingConfig(logger_name)
    logging_config.configure()

    return getLogger(logger_name)
