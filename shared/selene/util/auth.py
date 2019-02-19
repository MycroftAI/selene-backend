"""Logic for generating and validating JWT authentication tokens."""
from datetime import datetime
from time import time

import jwt


class AuthenticationError(Exception):
    pass


class AuthenticationToken(object):
    def __init__(self, secret: str, duration: int):
        self.secret = secret
        self.duration = duration
        self.jwt: str = ''
        self.is_valid: bool = None
        self.is_expired: bool = None
        self.account_id: str = None

    def generate(self):
        """
        Generates a JWT token
        """
        payload = dict(
            iat=datetime.utcnow(),
            exp=time() + self.duration,
            sub=self.account_id
        )
        token = jwt.encode(payload, self.secret, algorithm='HS256')

        # convert the token from byte-array to string so that
        # it can be included in a JSON response object
        self.jwt = token.decode()

    def validate(self):
        """Decodes the auth token and performs some preliminary validation."""
        self.is_expired = False
        self.is_valid = True

        if self.jwt is None:
            self.is_expired = True
        else:
            try:
                payload = jwt.decode(self.jwt, self.secret)
                self.account_id = payload['sub']
            except jwt.ExpiredSignatureError:
                self.is_expired = True
            except jwt.InvalidTokenError:
                self.is_valid = False
