from http import HTTPStatus
from logging import getLogger
import json

import requests

from selene.util.api import SeleneEndpoint, APIError

_log = getLogger(__package__)


class SkillInstallEndpoint(SeleneEndpoint):
    """
    Install a skill on user device(s).
    """
    def __init__(self):
        super(SkillInstallEndpoint, self).__init__()
        self.device_uuid: str = None
        self.installer_skill_settings: dict = {}
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
        service_request_parameters = {
            'disableHide': 'true'
        }
        service_url = (
            self.config['TARTARUS_BASE_URL'] +
            '/user/' +
            self.user_uuid +
            '/skill'
        )
        user_service_response = requests.get(
            service_url,
            headers=service_request_headers,
            params=service_request_parameters
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
        error_message = (
            'install failed: installer skill not found'
        )
        if "skills" in installed_skills:
            for skill in installed_skills['skills']:
                if skill['skill']['name'] == 'Installer' and self.validate_skill_installer(skill['skill']):
                    self.device_uuid = skill['deviceUuid']
                    installer_skill = skill['skill']
                    break
            if installer_skill is None:
                _log.error(error_message)
                self.response = (error_message, HTTPStatus.INTERNAL_SERVER_ERROR)
                raise APIError()
        else:
            _log.error(error_message)
            self.response = (error_message, HTTPStatus.INTERNAL_SERVER_ERROR)
            raise APIError()

        return installer_skill

    def validate_skill_installer(self, skill):
        has_to_install = False
        has_to_remove = False
        for field in skill['skillMetadata']['sections'][0]['fields']:
            if field['name'] == 'to_install':
                has_to_install = True
            elif field['name'] == 'to_remove':
                has_to_remove = True
        return has_to_install and has_to_remove

    def _find_installer_settings(self, installer_skill):
        for section in installer_skill['skillMetadata']['sections']:
            for setting in section['fields']:
                if setting['name'] == 'to_install':
                    self.installer_skill_settings['to_install'] = (setting['value'], setting['uuid'])
                elif setting['name'] == 'to_remove':
                    self.installer_skill_settings['to_remove'] = (setting['value'], setting['uuid'])

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

        section = self.request.json['section']
        skill_name = self.request.json['skill_name']

        devices = self._get_user_devices()

        setting_section = self.installer_skill_settings[section]
        if setting_section is not None:
            try:
                block = json.loads(setting_section[0])
            except ValueError:
                error_message = (
                    'found unexpected section: {}'
                )
                _log.error(error_message.format(setting_section[0]))
                raise ValueError(error_message.format(setting_section[0]))
            else:
                if not any(list(filter(lambda a: a['name'] == skill_name, block))):
                    block.append({'name': skill_name, 'devices': devices})

        else:
            error_message = (
                'found unexpected section {}'
            )
            _log.error(error_message.format(section))
            raise ValueError(error_message.format(section))
        install_request_body.append(
            dict(
                fieldUuid=setting_section[1],
                deviceUuid=self.device_uuid,
                value=json.dumps(block).replace('"', '\\"')
            )
        )
        return dict(batch=install_request_body)

    def _get_user_devices(self):
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        service_url = (
                self.config['TARTARUS_BASE_URL'] +
                '/user/' +
                self.user_uuid +
                '/device'
        )
        user_device_response = requests.get(service_url, headers=service_request_headers)

        if user_device_response.status_code != HTTPStatus.OK:
            self._check_for_service_errors(user_device_response)

        if user_device_response.content is not None:
            devices = json.loads(user_device_response.content)
            return list(map(lambda device: device['uuid'], devices))
        else:
            return []
