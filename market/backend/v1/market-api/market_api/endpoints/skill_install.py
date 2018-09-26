from http import HTTPStatus
from logging import getLogger
import json

from flask import current_app
import requests

from selene_util.api import SeleneBaseView, HTTPMethod, APIError

_log = getLogger(__package__)


class SkillInstallView(SeleneBaseView):
    """
    Install a skill on user device(s).
    """
    # Implemented as a PUT because installing a skill is actually an update
    # to the install skill's settings
    allowed_methods = [HTTPMethod.PUT]

    def __init__(self):
        super(SkillInstallView, self).__init__()
        self.user_uuid: str = None
        self.device_uuid: str = None
        self.installer_skill_settings: list = []
        self.installer_update_response = None

    def _get_data_to_update(self):
        installed_skills = self._get_installed_skills()
        installer_skill = self._find_installer_skill(installed_skills)
        self._find_installer_settings(installer_skill)

    def _get_installed_skills(self):
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        service_url = (
            current_app.config['TARTARUS_BASE_URL'] +
            '/user/' +
            self.user_uuid +
            '/skill'
        )
        user_service_response = requests.get(
            service_url,
            headers=service_request_headers
        )
        if user_service_response.status_code != HTTPStatus.OK:
            self._check_for_service_errors(user_service_response)
        if user_service_response.status_code == HTTPStatus.UNAUTHORIZED:
            # override response built in _build_service_error_response()
            # so that user knows there is a authentication issue
            self.response = (self.response[0], HTTPStatus.UNAUTHORIZED)
            raise APIError()

        return json.loads(user_service_response.content)

    def _find_installer_skill(self, installed_skills):
        installer_skill = None
        for skill in installed_skills['skills']:
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

    def _apply_update(self):
        service_url = current_app.config['TARTARUS_BASE_URL'] + '/skill/field'
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token,
            'Content-Type': 'application/json'
        }
        service_request_data = json.dumps(self._build_update_request_body())
        skill_service_response = requests.patch(
            service_url,
            data=service_request_data,
            headers=service_request_headers
        )
        if skill_service_response.status_code != HTTPStatus.OK:
            self._check_for_service_errors(skill_service_response)

        self.installer_update_response = json.loads(
            skill_service_response.content
        )

    def _build_update_request_body(self):
        install_request_body = []
        for setting in self.installer_skill_settings:
            if setting['name'] == 'installer_link':
                setting_value = self.request.json['skill_url']
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
                    fieldUuid=setting['uuid'],
                    deviceUuid=self.device_uuid,
                    value=setting_value
                )
            )

        return dict(batch=install_request_body)

    def _build_response_data(self):
        self.response_data = self.installer_update_response
