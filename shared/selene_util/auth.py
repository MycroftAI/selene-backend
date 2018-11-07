from datetime import datetime
from logging import getLogger
from time import time

import jwt

ONE_DAY = 2592000

_log = getLogger(__package__)


class AuthenticationError(Exception):
    pass


def encode_auth_token(secret_key, user_uuid):
    """
    Generates the Auth Token
    :return: string
    """
    token_expiration = time() + ONE_DAY
    payload = dict(iat=datetime.utcnow(), exp=token_expiration, sub=user_uuid)
    selene_token = jwt.encode(
        payload,
        secret_key,
        algorithm='HS256'
    )

    # before returning the token, convert it from bytes to string so that
    # it can be included in a JSON response object
    return selene_token.decode()


def decode_auth_token(auth_token: str, secret_key: str) -> tuple:
    """
    Decodes the auth token
    :param auth_token: the Selene JSON Web Token extracted from cookies.
    :param secret_key: the key needed to decode the token
    :return: two-value tuple containing a boolean value indicating if the
        token is good and the user UUID extracted from the token.  UUID will
        be None if token is invalid.
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
