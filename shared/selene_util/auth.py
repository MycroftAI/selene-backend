from logging import getLogger

import jwt

_log = getLogger(__package__)


class AuthenticationError(Exception):
    pass


def decode_auth_token(auth_token: str, secret_key: str) -> tuple:
    """
    Decodes the auth token
    :param auth_token: the Selene JSON Web Token extracted from the request cookies.
    :param secret_key: the key needed to decode the token
    :return: two-value tuple containing a boolean value indicating if the token is good and the
        user UUID extracted from the token.  UUID will be None if token is invalid.
    """
    try:
        payload = jwt.decode(auth_token, secret_key)
        user_uuid = payload['sub']
    except jwt.ExpiredSignatureError:
        error_msg = 'Selene token expired'
        _log.info(error_msg)
        raise AuthenticationError(error_msg)
    except jwt.InvalidTokenError:
        error_msg = 'Invalid Selene token'
        _log.info(error_msg)
        raise AuthenticationError(error_msg)

    return user_uuid
