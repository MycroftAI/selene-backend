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
        """
        Initialize the jwt.

        Args:
            self: (todo): write your description
            secret: (str): write your description
            duration: (todo): write your description
        """
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
    """
    Gets the account email.

    Args:
        token: (str): write your description
    """
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
    """
    Returns the account email.

    Args:
        token: (str): write your description
    """
    facebook_api = GraphAPI(token)
    facebook_account = facebook_api.get_object(id='me?fields=email')

    return facebook_account['email']


def get_github_account_email(token: str) -> str:
    """
    Retrieves the email.

    Args:
        token: (str): write your description
    """
    github_email = None
    github_user = requests.get(
        'https://api.github.com/user/emails',
        headers=dict(Authorization='token ' + token, Accept='application/json')
    )
    if github_user.status_code == HTTPStatus.OK:
        for email in json.loads(github_user.content):
            if email['primary']:
                github_email = email['email']

    return github_email


def get_github_authentication_token(access_code: str, state: str) -> str:
    """
    Get an access token from github.

    Args:
        access_code: (str): write your description
        state: (todo): write your description
    """
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

    return response_content.get('access_token')
