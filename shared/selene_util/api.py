"""Reusable code for the API layer"""
from http import HTTPStatus
from logging import getLogger

from flask import request, current_app
from flask_restful import Resource

from .auth import decode_auth_token, AuthorizationError


class ServiceUrlNotFound(Exception):
    pass


class ServiceServerError(Exception):
    pass


class MethodNotAllowedError(Exception):
    pass


class SeleneBaseView(Resource):
    """
    Install a skill on user device(s).
    """
    # The logger is initialized here but this should be overridden with a
    # package-specific logger (e.g. _log = getLogger(__package__)
    _log = getLogger()
    allowed_methods: str = None

    def __init__(self):
        self.base_url = current_app.config['SELENE_BASE_URL']
        self.response = None
        self.response_data = None
        self.tartarus_token: str = None
        self.selene_token: str = None
        self.service_response = None
        self.user_uuid: str = None
        self.user_is_authenticated: bool = False

    def get(self, *args):
        self._build_method_not_allowed_response('GET')

    def post(self):
        self._build_method_not_allowed_response('POST')

    def put(self):
        self._build_method_not_allowed_response('PUT')

    def delete(self):
        self._build_method_not_allowed_response('PUT')

    def _build_method_not_allowed_response(self, method):
        self.response(
            'HTTP {method} not implemented'.format(method=method),
            HTTPStatus.METHOD_NOT_ALLOWED,
            {'Allow': self.allowed_methods}
        )

    def _authenticate(self):
        self._get_auth_token()
        self._validate_auth_token()
        self.user_is_authenticated = True

    def _get_auth_token(self):
        try:
            self.selene_token = request.cookies['seleneToken']
            self.tartarus_token = request.cookies['tartarusToken']
        except KeyError:
            raise AuthorizationError(
                'no authentication token found in request'
            )

    def _validate_auth_token(self):
        self.user_uuid = decode_auth_token(
            self.selene_token,
            current_app.config['SECRET_KEY']
        )

    def check_for_service_errors(self, service, response):
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error_message = 'invalid authentication token'
            self._log.error(error_message)
            raise AuthorizationError(error_message)
        elif response.status_code == HTTPStatus.NOT_FOUND:
            error_message = '{service} service URL {url} not found'.format(
                service=service,
                url=response.request.url
            )
            self._log.error(error_message)
            raise ServiceUrlNotFound(error_message)
        elif response.status_code != HTTPStatus.OK:
            error_message = (
                '{service} service URL {url} HTTP status {status}'.format(
                    service=service,
                    status=response.status_code,
                    url=response.request.url
                )
            )
            self._log.error(error_message)
            raise ServiceServerError(error_message)

    def _build_response(self):
        try:
            self._build_response_data()
        except AuthorizationError as ae:
            self.response = (str(ae), HTTPStatus.UNAUTHORIZED)
        except ServiceUrlNotFound as nf:
            self.response = (str(nf), HTTPStatus.INTERNAL_SERVER_ERROR)
        except ServiceServerError as se:
            self.response = (str(se), HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            self.response = (self.response_data, HTTPStatus.OK)

    def _build_response_data(self):
        raise NotImplementedError
