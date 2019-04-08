"""Logic for generating and validating JWT authentication tokens."""
from datetime import datetime
from http import HTTPStatus
import json
from time import time

from facebook import GraphAPI
import jwt
import requests


class AuthenticationError(Exception):
    pass


class AuthenticationToken(object):
    # TODO: move duration argument to generate method
    def __init__(self, secret: str, duration: int):
        self.secret = secret
        self.duration = duration
        self.jwt: str = ''
        self.is_valid: bool = None
        self.is_expired: bool = None

    def generate(self, account_id):
        """
        Generates a JWT token
        """
        payload = dict(
            iat=datetime.utcnow(),
            exp=time() + self.duration,
            sub=account_id
        )
        token = jwt.encode(payload, self.secret, algorithm='HS256')

        # convert the token from byte-array to string so that
        # it can be included in a JSON response object
        self.jwt = token.decode()

    def validate(self):
        """Decodes the auth token and performs some preliminary validation."""
        self.is_expired = False
        self.is_valid = True
        account_id = None

        if self.jwt is None:
            self.is_expired = True
        else:
            try:
                payload = jwt.decode(self.jwt, self.secret)
                account_id = payload['sub']
            except jwt.ExpiredSignatureError:
                self.is_expired = True
            except jwt.InvalidTokenError:
                self.is_valid = False

        return account_id


def get_google_account_email(token):
    google_response = requests.get(
        'https://oauth2.googleapis.com/tokeninfo?id_token=' + token
    )
    if google_response.status_code == HTTPStatus.OK:
        google_account = json.loads(google_response.content)
        email_address = google_account['email']
    else:
        raise AuthenticationError('invalid Google token')

    return email_address


def get_facebook_account_email(token):
    facebook_api = GraphAPI(token)
    facebook_account = facebook_api.get_object(id='me?fields=email')
    return facebook_account['email']
