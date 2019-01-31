"""Authenticate a user logging in with a email address and password

This type of login is considered "internal" because we are storing the email
address and password on our servers.  This is as opposed to "external"
authentication, which uses a 3rd party authentication, like Google.

"""
from binascii import a2b_base64
from http import HTTPStatus
from time import time

from selene.api import SeleneEndpoint, APIError
from selene.util.auth import encode_auth_token, SEVEN_DAYS
from selene.util.db.connection_pool import get_db_connection
from selene.account.repository import get_account_id_from_credentials


class AuthenticateInternalEndpoint(SeleneEndpoint):
    """
    Sign in a user with an email address and password.
    """
    def __init__(self):
        super(AuthenticateInternalEndpoint, self).__init__()
        self.response_status_code = HTTPStatus.OK
        self.account_uuid = None

    def get(self):
        try:
            self._authenticate_credentials()
        except APIError:
            pass
        else:
            self._build_response()

        return self.response

    def _authenticate_credentials(self):
        """Compare credentials in request to credentials in database."""

        basic_credentials = self.request.headers['authorization']
        binary_credentials = a2b_base64(basic_credentials.strip('Basic '))
        email_address, password = binary_credentials.decode().split(':')
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            self.account_uuid = get_account_id_from_credentials(
                db,
                email_address,
                password
            )

    def _build_response(self):
        self.selene_token = encode_auth_token(
            self.config['SECRET_KEY'], self.account_uuid
        )
        response_data = dict(
            expiration=time() + SEVEN_DAYS,
            seleneToken=self.selene_token,
        )
        self.response = (response_data, HTTPStatus.OK)
