"""
Marketplace endpoint to add or remove a skill

This endpoint configures the install skill on a user's device(s) to add or
remove the skill.
"""
import ast
from http import HTTPStatus
from logging import getLogger
from typing import List

from schematics import Model
from schematics.types import StringType

from selene.api import ETagManager, SeleneEndpoint
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
    _settings_repo = None

    def __init__(self):
        super(SkillInstallEndpoint, self).__init__()
        self.installer_settings: List[AccountSkillSetting] = []
        self.skill_name = None
        self.etag_manager = ETagManager(
            self.config['SELENE_CACHE'],
            self.config
        )

    @property
    def settings_repo(self):
        if self._settings_repo is None:
            self._settings_repo = SkillSettingRepository(
                self.db,
                self.account.id
            )

        return self._settings_repo

    def put(self):
        """Handle an HTTP PUT request"""
        self._authenticate()
        self._validate_request()
        self._get_skill_name()
        self.installer_settings = self.settings_repo.get_installer_settings()
        self._apply_update()
        self.etag_manager.expire_skill_etag_by_account_id(self.account.id)

        return '', HTTPStatus.NO_CONTENT

    def _validate_request(self):
        """Ensure the data passed in the request is as expected.

        :raises schematics.exceptions.ValidationError if the validation fails
        """
        install_request = InstallRequest()
        install_request.setting_section = self.request.json['section']
        install_request.skill_display_id = self.request.json['skillDisplayId']
        install_request.validate()

    def _get_skill_name(self):
        """Get the name of the skill being installed/removed from the DB

        The installer skill expects the skill name found in the "name" field
        of the skill display JSON.
        """
        display_repo = SkillDisplayRepository(self.db)
        skill_display = display_repo.get_display_data_for_skill(
            self.request.json['skillDisplayId']
        )
        self.skill_name = skill_display.display_data['name']

    def _apply_update(self):
        """Add the skill in the request to the installer skill settings.

        This is designed to change the installer skill settings for all
        devices associated with an account.  It will be updated in the
        future to target specific devices.
        """
        section = self.request.json['section']
        for settings in self.installer_settings:
            setting_value = settings.settings_values.get(section, [])
            if isinstance(setting_value, str):
                setting_value = ast.literal_eval(setting_value)
            setting_value.append(dict(name=self.skill_name))
            settings.settings_values[section] = setting_value
            self._update_skill_settings(settings)

    def _update_skill_settings(self, new_skill_settings):
        """Update the DB with the new installer skill settings."""
        self.settings_repo.update_skill_settings(new_skill_settings)
