"""Defines a view that will install a skill on a device running Mycroft core"""\

from http import HTTPStatus
from logging import getLogger
import json

from flask import request, current_app
from flask_restful import Resource
import requests

from selene_util.auth import decode_auth_token, AuthorizationError

_log = getLogger(__package__)


class ServiceUrlNotFound(Exception):
    """Exception to call when a HTTP 404 status is returned."""
    pass


class ServiceServerError(Exception):
    """Catch all exception for errors not previously identified"""
    pass


class LogoutView(Resource):
    """Log a user out of the Mycroft web presence"""
    def __init__(self):
        self.service_response = None
        self.frontend_response = None
        self.user_uuid: str = None
        self.tartarus_token: str = None
        self.selene_token: str = None
        self.device_uuid = None
        self.installer_skill_settings = []

    def put(self):
        try:
            self._get_auth_tokens()
            self._validate_auth_token()
            self._logout()
        except AuthorizationError as ae:
            self._build_unauthorized_response(str(ae))
        except ServiceUrlNotFound as nf:
            self._build_server_error_response(str(nf))
        except ServiceServerError as se:
            self._build_server_error_response(str(se))
        else:
            self._build_success_response()

        return self.frontend_response

    def _get_auth_tokens(self):
        try:
            self.selene_token = request.cookies['seleneToken']
            self.tartarus_token = request.cookies['tartarusToken']
        except KeyError:
            raise AuthorizationError(
                'no authentication tokens found in request'
            )

    def _validate_auth_token(self):
        self.user_uuid = decode_auth_token(
            self.selene_token,
            current_app.config['SECRET_KEY']
        )

    def _logout(self):
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        service_url = current_app.config['TARTARUS_BASE_URL'] + '/auth/logout'
        service_response = requests.get(
            service_url,
            headers=service_request_headers
        )
        self.check_for_tartarus_errors(service_response, service_url)
        self.service_response_data = json.loads(service_response.content)

    def check_for_tartarus_errors(self, service_response, service_url):
        if service_response.status_code == HTTPStatus.UNAUTHORIZED:
            error_message = 'invalid Tartarus token'
            _log.error(error_message)
            raise AuthorizationError(error_message)
        elif service_response.status_code == HTTPStatus.NOT_FOUND:
            error_message = 'service url {} not found'.format(service_url)
            _log.error(error_message)
            raise ServiceUrlNotFound(error_message)
        elif service_response.status_code != HTTPStatus.OK:
            error_message = (
                'error occurred during request to {service} URL {url}'
            )
            _log.error(error_message.format(
                service='tartarus',
                url=service_url)
            )
            raise ServiceServerError(error_message)

    def _build_unauthorized_response(self, error_message):
        self.frontend_response = (
            dict(errorMessage=error_message),
            HTTPStatus.UNAUTHORIZED
        )

    def _build_server_error_response(self, error_message):
        self.frontend_response = (
            dict(errorMessage=error_message),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )

    def _build_success_response(self):
        service_response_data = json.loads(self.service_response.content)
        self.frontend_response = (
            dict(name=service_response_data.get('name')),
            HTTPStatus.OK
        )
