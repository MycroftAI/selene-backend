"""Reusable code for the API layer"""
from http import HTTPStatus
from logging import getLogger

from flask import request, current_app
from flask_restful import Resource

from .auth import decode_auth_token, AuthenticationError

# The logger is initialized here but this should be overridden with a
# package-specific logger (e.g. _log = getLogger(__package__)
_log = getLogger()


class APIError(Exception):
    """Raise this exception whenever a non-successful response is built"""
    pass


class SeleneResource(Resource):
    """
    Abstract base class for Selene Flask Restful API calls.

    Subclasses must do the following:
        -  override the allowed_methods class attribute to a list of all allowed
           HTTP methods.  Each list member must be a HTTPMethod enum
        -  override the _build_response_data method
    """
    authentication_required: bool = True
    config = current_app.config

    def __init__(self):
        self.authenticated = False
        self.request = request
        self.response = None
        self.selene_token: str = None
        self.tartarus_token: str = None
        self.user_uuid: str = None

    def _authenticate(self):
        """
        Authenticate the user using tokens passed via cookies.

        :raises: APIError()
        """
        try:
            self._get_auth_token()
            self._validate_auth_token()
        except AuthenticationError as ae:
            if self.authentication_required:
                self.response = (str(ae), HTTPStatus.UNAUTHORIZED)
                raise APIError()
        else:
            self.authenticated = True

    def _get_auth_token(self):
        """Get the Selene JWT (and the tartarus token) from cookies.

        :raises: AuthenticationError
        """
        try:
            self.selene_token = request.cookies['seleneToken']
            self.tartarus_token = request.cookies['tartarusToken']
        except KeyError:
            raise AuthenticationError(
                'no authentication token found in request'
            )

    def _validate_auth_token(self):
        """Decode the Selene JWT.

        :raises: AuthenticationError
        """
        self.user_uuid = decode_auth_token(
            self.selene_token,
            current_app.config['SECRET_KEY']
        )

    def _check_for_service_errors(self, service_response):
        """Common logic to handle non-successful returns from service calls."""
        if service_response.status_code != HTTPStatus.OK:
            error_message = (
                'service URL {url} returned HTTP status {status}'.format(
                    status=service_response.status_code,
                    url=service_response.request.url
                )
            )
            _log.error(error_message)
            if service_response.status_code == HTTPStatus.UNAUTHORIZED:
                self.response = (error_message, HTTPStatus.UNAUTHORIZED)
            else:
                self.response = (error_message, HTTPStatus.INTERNAL_SERVER_ERROR)
            raise APIError()
