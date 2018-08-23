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

    def __init__(self):
        self.base_url = current_app.config['SELENE_BASE_URL']
        self.response = None
        self.response_data = None
        self.tartarus_token: str = None
        self.selene_token: str = None
        self.service_response = None
        self.user_uuid: str = None

    def _authenticate(self):
        self._get_auth_token()
        self._validate_auth_token()

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
            self._build_unauthorized_response(str(ae))
        except ServiceUrlNotFound as nf:
            self._build_server_error_response(str(nf))
        except ServiceServerError as se:
            self._build_server_error_response(str(se))
        else:
            self._build_success_response()

    def _build_response_data(self):
        raise NotImplementedError

    def _build_unauthorized_response(self, error_message):
        self.response = (
            dict(errorMessage=error_message),
            HTTPStatus.UNAUTHORIZED
        )

    def _build_server_error_response(self, error_message):
        self.response = (
            dict(errorMessage=error_message),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )

    def _build_success_response(self):
            self.response = (self.response_data, HTTPStatus.OK)
