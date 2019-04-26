"""Logic for generating and validating JWT authentication tokens."""
from datetime import datetime
from http import HTTPStatus
import json
import os
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
        self.account_id = None
        self.is_valid: bool = None
        self.is_expired: bool = None

    def generate(self, account_id):
        """
        Generates a JWT token
        """
        self.account_id = account_id
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
        self.account_id = None

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


def get_google_account_email(token: str) -> str:
    google_response = requests.get(
        'https://oauth2.googleapis.com/tokeninfo?id_token=' + token
    )
    if google_response.status_code == HTTPStatus.OK:
        google_account = json.loads(google_response.content)
        email_address = google_account['email']
    else:
        raise AuthenticationError('invalid Google token')

    return email_address


def get_facebook_account_email(token: str) -> str:
    facebook_api = GraphAPI(token)
    facebook_account = facebook_api.get_object(id='me?fields=email')

    return facebook_account['email']


def get_github_account_email(token: str) -> str:
    github_user = requests.get(
        'https://api.github.com/user',
        headers=dict(Authorization='token ' + token, Accept='application/json')
    )
    response_content = json.loads(github_user.content)

    return response_content['email']


def get_github_authentication_token(access_code: str, state: str) -> str:
    params = [
        'client_id=' + os.environ['GITHUB_CLIENT_ID'],
        'client_secret=' + os.environ['GITHUB_CLIENT_SECRET'],
        'code=' + access_code,
        'state=' + state
    ]
    github_response = requests.post(
        'https://github.com/login/oauth/access_token?' + '&'.join(params),
        headers=dict(Accept='application/json')
    )
    response_content = json.loads(github_response.content)
    print(response_content)

    return response_content.get('access_token')
