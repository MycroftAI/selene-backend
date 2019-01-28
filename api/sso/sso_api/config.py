import os


class LoginConfigException(Exception):
    pass


class BaseConfig:
    """Base configuration."""
    DEBUG = False
    SECRET_KEY = os.environ['JWT_SECRET']
    SERVICE_BASE_URL = os.environ['SERVICE_BASE_URL']
    SSO_BASE_URL = os.environ['SSO_BASE_URL']
    TARTARUS_BASE_URL = os.environ['TARTARUS_BASE_URL']


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True


class TestConfig(BaseConfig):
    pass


class ProdConfig(BaseConfig):
    pass


def get_config_location():
    environment_configs = dict(
        dev=DevelopmentConfig,
        test=TestConfig,
        prod=ProdConfig
    )

    try:
        environment_name = os.environ['SELENE_ENVIRONMENT']
    except KeyError:
        raise LoginConfigException('the SELENE_ENVIRONMENT variable is not set')

    try:
        configs_location = environment_configs[environment_name]
    except KeyError:
        raise LoginConfigException(
            'no configuration defined for the "{}" environment'.format(environment_name)
        )

    return configs_location
