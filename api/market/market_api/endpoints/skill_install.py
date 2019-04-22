from http import HTTPStatus
from logging import getLogger
from typing import List

from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.data.skill import AccountSkillSetting, SkillSettingRepository

INSTALL_SECTION = 'to_install'
UNINSTALL_SECTION = 'to_remove'

_log = getLogger(__package__)


class InstallRequest(Model):
    setting_section = StringType(
        required=True,
        choices=[INSTALL_SECTION, UNINSTALL_SECTION]
    )
    skill_name = StringType(required=True)


class SkillInstallEndpoint(SeleneEndpoint):
    """
    Install a skill on user device(s).
    """
    def __init__(self):
        super(SkillInstallEndpoint, self).__init__()
        self.device_uuid: str = None
        self.installer_settings: List[AccountSkillSetting] = []
        self.installer_skill_settings: dict = {}
        self.installer_update_response = None

    def put(self):
        self._authenticate()
        self._validate_request()
        self._get_installer_settings()
        self._apply_update()
        self.response = (self.installer_update_response, HTTPStatus.OK)

        return self.response

    def _validate_request(self):
        install_request = InstallRequest()
        install_request.setting_section = self.request.json['section']
        install_request.skill_name = self.request.json['skillName']
        install_request.validate()

    def _get_installer_settings(self):
        settings_repo = SkillSettingRepository(self.db)
        self.installer_settings = settings_repo.get_installer_settings(
            self.account.id
        )

    def _apply_update(self):
        for settings in self.installer_settings:
            if self.request.json['section'] == INSTALL_SECTION:
                to_install = settings.settings_values.get(INSTALL_SECTION, [])
                to_install.append(
                    dict(name=self.request.json['skill_name'])
                )
                settings.settings_values[INSTALL_SECTION] = to_install
            else:
                to_remove = settings.settings_values.get(UNINSTALL_SECTION, [])
                to_remove.append(
                    dict(name=self.request.json['skill_name'])
                )
                settings.settings_values[UNINSTALL_SECTION] = to_remove
            self._update_skill_settings(settings)

    def _update_skill_settings(self, settings):
        settings_repo = SkillSettingRepository(self.db)
        settings_repo.update_device_skill_settings(
            self.account.id,
            settings.devices,
            settings.settings_values
        )
