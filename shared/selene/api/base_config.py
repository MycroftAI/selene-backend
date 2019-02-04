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

db_connection_config = DatabaseConnectionConfig(
    host=os.environ['DB_HOST'],
    db_name=os.environ['DB_NAME'],
    password=os.environ['DB_PASSWORD'],
    port=os.environ.get('DB_PORT', 5432),
    user=os.environ['DB_USER']
)


class APIConfigError(Exception):
    pass


class BaseConfig(object):
    """Base configuration."""
    ACCESS_SECRET = os.environ['JWT_ACCESS_SECRET']
    DB_CONNECTION_POOL = allocate_db_connection_pool(db_connection_config)
    DEBUG = False
    ENV = os.environ['SELENE_ENVIRONMENT']
    REFRESH_SECRET = os.environ['JWT_REFRESH_SECRET']


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DOMAIN = '.localhost'


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
