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

"""Define configuration values that apply to all Mycroft Flask APIs

The below base config classes included in this module represent globally
applicable config values.  Please do not add to these classes unless the new
config applies to ALL APIs. Define additional configs specific to an
application within the application..

Example usage:
    in api.py:
        from selene.api import get_environment_config
        app.config = from_object(get_base_config())
        app.config.update(<app_specific_configs>)
        .
        .
        .
        @app.teardown_appcontext
        def close_db_connections():
            app.config['DB_CONNECTION_POOL'].close_all()
"""

import os

from selene.util.db import allocate_db_connection_pool, DatabaseConnectionConfig


class APIConfigError(Exception):
    pass


class BaseConfig(object):
    """Base configuration."""
    ACCESS_SECRET = os.environ['JWT_ACCESS_SECRET']
    DB_CONNECTION_POOL = None
    DEBUG = False
    ENV = os.environ['SELENE_ENVIRONMENT']
    REFRESH_SECRET = os.environ['JWT_REFRESH_SECRET']
    DB_CONNECTION_CONFIG = DatabaseConnectionConfig(
        host=os.environ['DB_HOST'],
        db_name=os.environ['DB_NAME'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ.get('DB_PORT', 5432),
        user=os.environ['DB_USER'],
        sslmode=os.environ.get('DB_SSLMODE')
    )


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DOMAIN = '.mycroft.test'


class TestConfig(BaseConfig):
    DOMAIN = '.mycroft-test.net'


class ProdConfig(BaseConfig):
    DOMAIN = '.mycroft.ai'


def get_base_config():
    """Determine which config object to pass to the application.

    :return: an object containing the configs for the API.
    """
    environment_configs = dict(
        dev=DevelopmentConfig,
        test=TestConfig,
        prod=ProdConfig
    )

    try:
        environment_name = os.environ['SELENE_ENVIRONMENT']
    except KeyError:
        raise APIConfigError('the SELENE_ENVIRONMENT variable is not set')

    try:
        app_config = environment_configs[environment_name]
    except KeyError:
        error_msg = 'no configuration defined for the "{}" environment'
        raise APIConfigError(error_msg.format(environment_name))

    return app_config
