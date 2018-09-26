"""Reusable code for the API layer"""
from enum import Enum
from http import HTTPStatus
from logging import getLogger

from flask import request, current_app
from flask_restful import Resource

from .auth import decode_auth_token, AuthenticationError

# The logger is initialized here but this should be overridden with a
# package-specific logger (e.g. _log = getLogger(__package__)
_log = getLogger()


class HTTPMethod(Enum):
    DELETE = 'DELETE'
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'


class APIError(Exception):
    pass


class SeleneBaseView(Resource):
    """
    Abstract base class for Selene Flask Restful API calls.

    Subclasses must do the following:
        -  override the allowed_methods class attribute to a list of all allowed
           HTTP methods.  Each list member must be a HTTPMethod enum
        -  override the _build_response_data method
    """
    allowed_methods: list = None

    def __init__(self):
        self.base_url = current_app.config['SELENE_BASE_URL']
        self.authentication_required: bool = True
        self.response = None
        self.response_data = None
        self.selene_token: str = None
        self.service_response = None
        self.tartarus_token: str = None
        self.user_uuid: str = None

    def get(self, *args):
        """Handle a HTTP GET request."""
        self._process_api_request(HTTPMethod.GET)
        return self.response

    def post(self):
        """Handle a HTTP POST request."""
        self._process_api_request(HTTPMethod.POST)
        return self.response

    def put(self):
        """Handle a HTTP PUT request."""
        self._process_api_request(HTTPMethod.PUT)
        return self.response

    def delete(self):
        """Handle a HTTP DELETE request."""
        self._process_api_request(HTTPMethod.DELETE)
        return self.response

    def _process_api_request(self, http_method):
        if http_method in self.allowed_methods:
            try:
                self._authenticate()
                if http_method == HTTPMethod.GET:
                    self._get_requested_data()
                self._build_response_data()
            except APIError:
                # the response object should have been built when the error
                # was encountered so no action is needed here
                pass
            else:
                self.response = (self.response_data, HTTPStatus.OK)
        else:
            self.response = (
                'HTTP {} not implemented'.format(http_method.value),
                HTTPStatus.METHOD_NOT_ALLOWED,
                {'Allow': ','.join(self.allowed_methods)}
            )

    def _authenticate(self):
        """
        Authenticate the user using tokens passed via cookies.

        :raises: APIError()
        """
        try:
            self._get_auth_token()
            self._validate_auth_token()
        except AuthenticationError as ae:
            self.response = (str(ae), HTTPStatus.UNAUTHORIZED)
            raise APIError()

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

    def _get_requested_data(self):
        """Override this method for GET requests."""
        pass

    def _build_response_data(self):
        """Override for all HTTP methods; build the response when successful"""
        raise NotImplementedError

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
            self.response = (error_message, HTTPStatus.INTERNAL_SERVER_ERROR)
            raise APIError()
