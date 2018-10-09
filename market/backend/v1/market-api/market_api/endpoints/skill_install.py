from http import HTTPStatus
from logging import getLogger
import json

import requests

from selene_util.api import SeleneEndpoint, APIError

_log = getLogger(__package__)


class SkillInstallEndpoint(SeleneEndpoint):
    """
    Install a skill on user device(s).
    """
    def __init__(self):
        super(SkillInstallEndpoint, self).__init__()
        self.device_uuid: str = None
        self.installer_skill_settings: list = []
        self.installer_update_response = None

    def put(self):
        try:
            self._authenticate()
            self._get_installer_skill()
            self._apply_update()
        except APIError:
            pass
        else:
            self.response = (self.installer_update_response, HTTPStatus.OK)

        return self.response

    def _get_installer_skill(self):
        installed_skills = self._get_installed_skills()
        installer_skill = self._find_installer_skill(installed_skills)
        self._find_installer_settings(installer_skill)

    def _get_installed_skills(self):
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        service_url = (
            self.config['TARTARUS_BASE_URL'] +
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
        service_url = self.config['TARTARUS_BASE_URL'] + '/skill/field'
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
