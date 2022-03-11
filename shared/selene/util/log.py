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

from os import environ
import logging.config


def _generate_log_config(service: str) -> dict:
    """Uses Python's dictionary config for logging to setup Selene logs.

    Args:
        service: the name of the service initiating the log setup

    Returns:
        The logging configuration in dictionary format.
    """
    log_format = (
        "{asctime} | {levelname:8} | {process:5} | {name}.{funcName} | {message}"
    )
    default_formatter = {"format": log_format, "style": "{"}
    console_handler = {
        "class": "logging.StreamHandler",
        "formatter": "default",
        "stream": "ext://sys.stdout",
    }
    file_handler = {
        "class": "logging.handlers.TimedRotatingFileHandler",
        "formatter": "default",
        "filename": f"/var/log/mycroft/{service}.log",
        "backupCount": 30,
        "when": "midnight",
    }

    return {
        "version": 1,
        "formatters": {"default": default_formatter},
        "handlers": {"console": console_handler, "file": file_handler},
        "root": {"level": "INFO", "handlers": ["file"]},
    }


def configure_selene_logger(service):
    """Configures the base logger for any Selene service or application.

    Args:
        service: the name of the service initiating the log setup
    """
    log_level = environ.get("SELENE_LOG_LEVEL", "INFO")
    log_config = _generate_log_config(service)
    selene_logger = {
        "selene": {"level": log_level, "handlers": ["console", "file"], "propagate": 0}
    }
    log_config["loggers"] = selene_logger
    logging.config.dictConfig(log_config)
    logging.getLogger("selene")


def get_selene_logger(module_name: str):
    """Returns a logger instance based on the Selene logger."""
    return logging.getLogger("selene." + module_name)
