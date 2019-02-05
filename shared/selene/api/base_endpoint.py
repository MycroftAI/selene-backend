"""Base class for Flask API endpoints"""

from http import HTTPStatus

from flask import after_this_request, current_app, request
from flask_restful import Resource

from selene.account import Account, AccountRepository, RefreshTokenRepository
from selene.util.auth import (
    AuthenticationError,
    AuthenticationTokenGenerator,
    AuthenticationTokenValidator,
    FIFTEEN_MINUTES,
    ONE_MONTH
)
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
        self.access_token_expired: bool = False
        self.refresh_token_expired: bool = False
        self.account: Account = None

    def _authenticate(self):
        """
        Authenticate the user using tokens passed via cookies.

        :raises: APIError()
        """
        try:
            account_id = self._validate_auth_tokens()
            self._validate_account(account_id)
        except AuthenticationError as ae:
            if self.authentication_required:
                self.response = (str(ae), HTTPStatus.UNAUTHORIZED)
                raise APIError()
        else:
            self.authenticated = True

    def _validate_auth_tokens(self) -> str:
        self.access_token_expired, account_id = self._validate_token(
            'seleneAccess',
            self.config['ACCESS_TOKEN_SECRET']
        )
        if self.access_token_expired:
            self.refresh_token_expired, account_id = self._validate_token(
                'seleneRefresh',
                self.config['REFRESH_TOKEN_SECRET']
            )

        return account_id

    def _validate_token(self, cookie_key, jwt_secret):
        """Validate the access token is well-formed and not expired

        :raises: AuthenticationError
        """
        account_id = None
        token_expired = False

        try:
            access_token = self.request.cookies[cookie_key]
        except KeyError:
            error_msg = 'no {} token found in request'
            raise AuthenticationError(error_msg.format(cookie_key))

        validator = AuthenticationTokenValidator(access_token, jwt_secret)
        validator.validate_token()
        if validator.token_is_expired:
            token_expired = True
        elif validator.token_is_invalid:
            raise AuthenticationError('access token is invalid')
        else:
            account_id = validator.account_id

        return token_expired, account_id

    def _validate_account(self, account_id):
        """The refresh token in the request must match the database value.

        :raises: AuthenticationError
        """
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account_repository = AccountRepository(db)
            self.account = account_repository.get_account_by_id(account_id)

        if self.account is None:
            raise AuthenticationError('account not found')

        if self.access_token_expired:
            if self.refresh_token not in self.account.refresh_tokens:
                raise AuthenticationError('refresh token not found')

    def _generate_tokens(self):
        token_generator = AuthenticationTokenGenerator(
            self.account.id,
            self.config['ACCESS_SECRET'],
            self.config['REFRESH_SECRET']
        )
        access_token = token_generator.access_token
        refresh_token = token_generator.refresh_token

        return access_token, refresh_token

    def _generate_token_cookies(self, access_token, refresh_token):
        access_token_cookie = dict(
            key='seleneAccess',
            value=str(access_token),
            domain=self.config['DOMAIN'],
            max_age=FIFTEEN_MINUTES,
        )
        refresh_token_cookie = dict(
            key='seleneRefresh',
            value=str(refresh_token),
            domain=self.config['DOMAIN'],
            max_age=ONE_MONTH,
        )

        @after_this_request
        def set_cookies(response):
            response.set_cookie(**access_token_cookie)
            response.set_cookie(**refresh_token_cookie)

            return response

    def _update_refresh_token_on_db(self, new_refresh_token):
        old_refresh_token = self.request.cookies['seleneRefresh']
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            token_repository = RefreshTokenRepository(db, self.account)
            if self.refresh_token_expired:
                token_repository.delete_refresh_token(old_refresh_token)
                raise AuthenticationError('refresh token expired')
            else:
                token_repository.update_refresh_token(
                    new_refresh_token,
                    old_refresh_token
                )
