"""
Marketplace endpoint to add or remove a skill

This endpoint configures the install skill on a user's device(s) to add or
remove the skill.
"""
from http import HTTPStatus
from logging import getLogger
from typing import List

from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.data.skill import (
    AccountSkillSetting,
    SkillDisplayRepository,
    SkillSettingRepository
)

INSTALL_SECTION = 'to_install'
UNINSTALL_SECTION = 'to_remove'

_log = getLogger(__package__)


class InstallRequest(Model):
    """Defines the expected state of the request JSON data"""
    setting_section = StringType(
        required=True,
        choices=[INSTALL_SECTION, UNINSTALL_SECTION]
    )
    skill_display_id = StringType(required=True)


class SkillInstallEndpoint(SeleneEndpoint):
    """Install a skill on user device(s)."""
    def __init__(self):
        super(SkillInstallEndpoint, self).__init__()
        self.device_uuid: str = None
        self.installer_settings: List[AccountSkillSetting] = []
        self.installer_skill_settings: dict = {}
        self.installer_update_response = None

    def put(self):
        """Handle an HTTP PUT request"""
        self._authenticate()
        self._validate_request()
        skill_install_name = self._get_install_name()
        self._get_installer_settings()
        self._apply_update(skill_install_name)
        self.response = (self.installer_update_response, HTTPStatus.OK)

        return self.response

    def _validate_request(self):
        """Ensure the data passed in the request is as expected.

        :raises schematics.exceptions.ValidationError if the validation fails
        """
        install_request = InstallRequest()
        install_request.setting_section = self.request.json['section']
        install_request.skill_display_id = self.request.json['skillDisplayId']
        install_request.validate()

    def _get_install_name(self) -> str:
        """Get the skill name used by the installer skill from the DB

        The installer skill expects the skill name found in the "name" field
        of the skill display JSON.
        """
        display_repo = SkillDisplayRepository(self.db)
        skill_display = display_repo.get_display_data_for_skill(
            self.request.json['skillDisplayId']
        )

        return skill_display.display_data['name']

    def _get_installer_settings(self):
        """Get the current value of the installer skill's settings"""
        settings_repo = SkillSettingRepository(self.db)
        self.installer_settings = settings_repo.get_installer_settings(
            self.account.id
        )

    def _apply_update(self, skill_install_name: str):
        """Add the skill in the request to the installer skill settings.

        This is designed to change the installer skill settings for all
        devices associated with an account.  It will be updated in the
        future to target specific devices.
        """
        for settings in self.installer_settings:
            if self.request.json['section'] == INSTALL_SECTION:
                to_install = settings.settings_values.get(INSTALL_SECTION, [])
                to_install.append(
                    dict(name=skill_install_name)
                )
                settings.settings_values[INSTALL_SECTION] = to_install
            else:
                to_remove = settings.settings_values.get(UNINSTALL_SECTION, [])
                to_remove.append(
                    dict(name=skill_install_name)
                )
                settings.settings_values[UNINSTALL_SECTION] = to_remove
            self._update_skill_settings(settings)

    def _update_skill_settings(self, settings):
        """Update the DB with the new installer skill settings."""
        settings_repo = SkillSettingRepository(self.db)
        settings_repo.update_device_skill_settings(
            self.account.id,
            settings.devices,
            settings.settings_values
        )
