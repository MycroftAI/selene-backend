from http import HTTPStatus
from logging import getLogger
import json

from flask import request, current_app
from flask_restful import Resource
import requests

from selene_util.auth import decode_auth_token, AuthorizationError

_log = getLogger(__package__)


class ServiceUrlNotFound(Exception):
    pass


class ServiceServerError(Exception):
    pass


class SkillInstallView(Resource):
    """
    Install a skill on user device(s).
    """
    def __init__(self):
        self.service_response = None
        self.frontend_response = None
        self.frontend_response_status_code = HTTPStatus.OK
        self.user_uuid: str = None
        self.tartarus_token: str = None
        self.selene_token: str = None
        self.device_uuid = None
        self.installer_skill_settings = []

    def put(self):
        try:
            self._get_auth_tokens()
            self._validate_auth_token()
            self._install_skill()
        except AuthorizationError as ae:
            self._build_unauthorized_response(str(ae))
        except ServiceUrlNotFound as nf:
            self._build_server_error_response(str(nf))
        except ServiceServerError as se:
            self._build_server_error_response(str(se))
        else:
            self._build_frontend_response()

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

    def _install_skill(self):
        self._get_users_installer_skill_settings()
        installer_skill = self._find_installer_skill()
        self._find_installer_settings(installer_skill)
        self._update_skill_installer_settings()

    def _get_users_installer_skill_settings(self):
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        service_url = (
            current_app.config['TARTARUS_BASE_URL'] +
            '/user/' +
            self.user_uuid +
            '/skill'
        )
        self.service_response = requests.get(
            service_url,
            headers=service_request_headers
        )
        self.check_for_tartarus_errors(service_url)

    def _find_installer_skill(self):
        service_response_data = json.loads(self.service_response.content)
        installer_skill = None
        for skill in service_response_data['skills']:
            if skill['skill']['name'] == 'Installer':
                self.device_uuid = skill['deviceUuid']
                installer_skill = skill['skill']
                break

        return installer_skill

    def _find_installer_settings(self, installer_skill):
        for section in installer_skill['skillMetadata']['sections']:
            for setting in section['fields']:
                if setting['type'] != 'label':
                    self.installer_skill_settings.append(setting)

    def _update_skill_installer_settings(self):
        service_url = current_app.config['TARTARUS_BASE_URL'] + '/skill/field'
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        self.service_response = requests.patch(
            service_url,
            data=json.dumps(self._build_install_request_body()),
            headers=service_request_headers
        )
        self.check_for_tartarus_errors(service_url)

    def _build_install_request_body(self):
        install_request_body = []
        for setting in self.installer_skill_settings:
            if setting['name'] == 'installer_link':
                setting_value = 'foo'
            elif setting['name'] == 'auto_install':
                setting_value = True
            else:
                error_message = (
                    'found unexpected setting "{}" in installer skill settings'
                )
                _log.error(error_message.format(setting['name']))
                raise ValueError(error_message.format(setting['name']))
            install_request_body.append(
                dict(
                    fieldUiud=setting['uuid'],
                    deviceUuid=self.device_uuid, value=setting_value
                )
            )
        return dict(batch=install_request_body)

    def check_for_tartarus_errors(self, service_url):
        if self.service_response.status_code == HTTPStatus.UNAUTHORIZED:
            error_message = 'invalid Tartarus token'
            _log.error(error_message)
            raise AuthorizationError(error_message)
        elif self.service_response.status_code == HTTPStatus.NOT_FOUND:
            error_message = 'service url {} not found'.format(service_url)
            _log.error(error_message)
            raise ServiceUrlNotFound(error_message)
        elif self.service_response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            error_message = (
                'error occurred during GET request to URL ' + service_url
            )
            _log.error(error_message)
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

    def _build_frontend_response(self):
        if self.service_response.status_code == HTTPStatus.OK:
            service_response_data = json.loads(self.service_response.content)
            self.frontend_response = (
                dict(name=service_response_data.get('name')),
                HTTPStatus.OK
            )
        elif self.service_response.status_code == HTTPStatus.NOT_FOUND:
            error_message = 'service url {} not found'
            _log.error(error_message)
            self.frontend_response = (
                dict(error_message=error_message),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )
        else:
            self.frontend_response = ({}, self.service_response.status_code)
