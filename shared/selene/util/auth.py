from datetime import datetime
from time import time

import jwt

FIFTEEN_MINUTES = 900
ONE_MONTH = 2628000


class AuthenticationError(Exception):
    pass


class AuthenticationTokenGenerator(object):
    _access_token = None
    _refresh_token = None

    def __init__(self, account_id: str):
        self.account_id = account_id
        self.access_secret = None
        self.refresh_secret = None

    def _generate_token(self, token_duration: int):
        """
        Generates a JWT token
        """
        token_expiration = time() + token_duration
        payload = dict(
            iat=datetime.utcnow(),
            exp=token_expiration,
            sub=self.account_id
        )

        if token_duration == FIFTEEN_MINUTES:
            secret = self.access_secret
        else:
            secret = self.refresh_secret

        if secret is None:
            raise ValueError('cannot generate a token without a secret')

        token = jwt.encode(
            payload,
            secret,
            algorithm='HS256'
        )

        # convert the token from byte-array to string so that
        # it can be included in a JSON response object
        return token.decode()

    @property
    def access_token(self):
        """
        Generates a JWT access token
        """
        if self._access_token is None:
            self._access_token = self._generate_token(FIFTEEN_MINUTES)

        return self._access_token

    @property
    def refresh_token(self):
        """
        Generates a JWT access token
        """
        if self._refresh_token is None:
            self._refresh_token = self._generate_token(ONE_MONTH)

        return self._refresh_token


class AuthenticationTokenValidator(object):
    def __init__(self, token: str, secret: str):
        self.token = token
        self.secret = secret
        self.account_id = None
        self.token_is_expired = False
        self.token_is_invalid = False

    def validate_token(self):
        """Decodes the auth token"""
        try:
            payload = jwt.decode(self.token, self.secret)
            self.account_id = payload['sub']
        except jwt.ExpiredSignatureError:
            self.token_is_expired = True
        except jwt.InvalidTokenError:
            self.token_is_invalid = True
