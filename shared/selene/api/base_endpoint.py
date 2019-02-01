"""Base class for Flask API endpoints"""

from http import HTTPStatus

from flask import request, current_app
from flask_restful import Resource

from selene.account import AccountRepository
from selene.util.auth import AuthenticationError, AuthenticationTokenValidator
from selene.util.db import get_db_connection


class APIError(Exception):
    """Raise this exception whenever a non-successful response is built"""
    pass


class SeleneEndpoint(Resource):
    """
    Abstract base class for Selene Flask Restful API calls.

    Subclasses must do the following:
        -  override the allowed_methods class attribute to a list of all allowed
           HTTP methods.  Each list member must be a HTTPMethod enum
        -  override the _build_response_data method
    """
    authentication_required: bool = True

    def __init__(self):
        self.config: dict = current_app.config
        self.authenticated = False
        self.request = request
        self.response: tuple = None
        self.access_token: str = None
        self.access_token_expired: bool = False
        self.account_id: str = None

    def _authenticate(self):
        """
        Authenticate the user using tokens passed via cookies.

        :raises: APIError()
        """
        try:
            self._get_access_token()
            self._validate_access_token()
            if self.access_token_expired:
                self._get_refresh_token()
                self._validate_refresh_token()
                self._compare_token_to_db()
        except AuthenticationError as ae:
            if self.authentication_required:
                self.response = (str(ae), HTTPStatus.UNAUTHORIZED)
                raise APIError()
        else:
            self.authenticated = True

    def _get_access_token(self):
        """Get the Selene JWT access tokens from request cookies.

        :raises: AuthenticationError
        """
        try:
            self.access_token = self.request.cookies['seleneAccess']
        except KeyError:
            raise AuthenticationError('no access token found in request')

    def _validate_access_token(self):
        """Validate the access token is well-formed and not expired

        :raises: AuthenticationError
        """
        validator = AuthenticationTokenValidator(
            self.access_token,
            self.config['ACCESS_TOKEN_SECRET']
        )
        validator.validate_token()
        if validator.token_is_expired:
            self.access_token_expired = True
        elif validator.token_is_invalid:
            raise AuthenticationError('access token is invalid')
        else:
            self.account_id = validator.account_id

    def _get_refresh_token(self):
        """Get the Selene JWT refresh tokens from request cookies.

        :raises: AuthenticationError
        """
        try:
            self.refresh_token = self.request.cookies['seleneRefresh']
        except KeyError:
            raise AuthenticationError('no refresh token found in request')

    def _validate_refresh_token(self):
        """Validate the refresh token is well-formed and not expired

        :raises: AuthenticationError
        """
        validator = AuthenticationTokenValidator(
            self.refresh_token,
            self.config['REFRESH_TOKEN_SECRET']
        )
        validator.validate_token()
        if validator.token_is_expired:
            raise AuthenticationError('refresh token is expired')
        elif validator.token_is_invalid:
            raise AuthenticationError('access token is invalid')
        else:
            self.account_id = validator.account_id

    def _compare_token_to_db(self):
        """The refresh token in the request must match the database value.

        :raises: AuthenticationError
        """
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account_repository = AccountRepository(db)
            account = account_repository.get_account_by_id(self.account_id)

        if account.refresh_token != self.refreshToken:
            raise AuthenticationError('refresh token not recognized')
