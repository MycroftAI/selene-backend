# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Data repository code for the skills on a device"""
import json
from dataclasses import asdict
from typing import List

from selene.data.skill import SettingsDisplay
from ..entity.device_skill import (
    AccountSkillSettings,
    DeviceSkillSettings,
    ManifestSkill
)
from ...repository_base import RepositoryBase


class DeviceSkillRepository(RepositoryBase):
    def __init__(self, db):
        """
        Initialize the database.

        Args:
            self: (todo): write your description
            db: (todo): write your description
        """
        super(DeviceSkillRepository, self).__init__(db, __file__)

    def get_skill_settings_for_account(
            self, account_id: str, skill_id: str
    ) -> List[AccountSkillSettings]:
        """
        Gets all settings for a particular account.

        Args:
            self: (todo): write your description
            account_id: (str): write your description
            skill_id: (str): write your description
        """
        return self._select_all_into_dataclass(
            AccountSkillSettings,
            sql_file_name='get_skill_settings_for_account.sql',
            args=dict(account_id=account_id, skill_id=skill_id)
        )

    def get_skill_settings_for_device(self, device_id, skill_id=None):
        """
        Return the skill settings for skill.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
            skill_id: (str): write your description
        """
        device_skills = self._select_all_into_dataclass(
            DeviceSkillSettings,
            sql_file_name='get_skill_settings_for_device.sql',
            args=dict(device_id=device_id)
        )
        if skill_id is None:
            skill_settings = device_skills
        else:
            skill_settings = None
            for skill in device_skills:
                if skill.skill_id == skill_id:
                    skill_settings = skill
                    break

        return skill_settings

    def update_skill_settings(
            self, account_id: str, device_names: tuple, skill_name: str
    ):
        """
        Update skill settings.

        Args:
            self: (todo): write your description
            account_id: (str): write your description
            device_names: (str): write your description
            skill_name: (str): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='update_skill_settings.sql',
            args=dict(
                account_id=account_id,
                device_names=device_names,
                skill_name=skill_name
            )
        )
        self.cursor.update(db_request)

    def upsert_device_skill_settings(
            self,
            device_ids: List[str],
            settings_display: SettingsDisplay,
            settings_values: dict,
    ):
        """
        Ups settings into device settings.

        Args:
            self: (todo): write your description
            device_ids: (int): write your description
            settings_display: (str): write your description
            settings_values: (todo): write your description
        """
        for device_id in device_ids:
            if settings_values is None:
                db_settings_values = None
            else:
                db_settings_values = json.dumps(settings_values)
            db_request = self._build_db_request(
                sql_file_name='upsert_device_skill_settings.sql',
                args=dict(
                    device_id=device_id,
                    skill_id=settings_display.skill_id,
                    settings_values=db_settings_values,
                    settings_display_id=settings_display.id
                )
            )
            self.cursor.insert(db_request)

    def update_device_skill_settings(self, device_id, device_skill):
        """Update the skill settings columns on the device_skill table."""
        if device_skill.settings_values is None:
            db_settings_values = None
        else:
            db_settings_values = json.dumps(device_skill.settings_values)
        db_request = self._build_db_request(
            sql_file_name='update_device_skill_settings.sql',
            args=dict(
                device_id=device_id,
                skill_id=device_skill.skill_id,
                settings_display_id=device_skill.settings_display_id,
                settings_values=db_settings_values
            )
        )
        self.cursor.update(db_request)

    def get_skill_manifest_for_device(
            self, device_id: str
    ) -> List[ManifestSkill]:
        """
        Returns a device manifest for a manifest.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
        """
        return self._select_all_into_dataclass(
            dataclass=ManifestSkill,
            sql_file_name='get_device_skill_manifest.sql',
            args=dict(device_id=device_id)
        )

    def get_skill_manifest_for_account(
            self, account_id: str
    ) -> List[ManifestSkill]:
        """
        Gets a manifest for a given account.

        Args:
            self: (todo): write your description
            account_id: (str): write your description
        """
        return self._select_all_into_dataclass(
            dataclass=ManifestSkill,
            sql_file_name='get_skill_manifest_for_account.sql',
            args=dict(account_id=account_id)
        )

    def update_manifest_skill(self, manifest_skill: ManifestSkill):
        """
        Updates the manifest

        Args:
            self: (todo): write your description
            manifest_skill: (todo): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='update_skill_manifest.sql',
            args=asdict(manifest_skill)
        )

        self.cursor.update(db_request)

    def add_manifest_skill(self, manifest_skill: ManifestSkill):
        """
        Adds a manifest to the manifest.

        Args:
            self: (todo): write your description
            manifest_skill: (str): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='add_manifest_skill.sql',
            args=asdict(manifest_skill)
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result['id']

    def remove_manifest_skill(self, manifest_skill: ManifestSkill):
        """
        Removes the manifest from the manifest.

        Args:
            self: (todo): write your description
            manifest_skill: (str): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='remove_manifest_skill.sql',
            args=dict(
                device_id=manifest_skill.device_id,
                skill_gid=manifest_skill.skill_gid
            )
        )
        self.cursor.delete(db_request)

    def get_settings_display_usage(self, settings_display_id: str) -> int:
        """
        Return the display usage for the database.

        Args:
            self: (todo): write your description
            settings_display_id: (str): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='get_settings_display_usage.sql',
            args=dict(settings_display_id=settings_display_id)
        )
        db_result = self.cursor.select_one(db_request)

        return db_result['usage']

    def remove(self, device_id, skill_id):
        """
        Removes the skill.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
            skill_id: (str): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='delete_device_skill.sql',
            args=dict(
                device_id=device_id,
                skill_id=skill_id
            )
        )
        self.cursor.delete(db_request)
