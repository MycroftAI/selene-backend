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

from datetime import datetime
from http import HTTPStatus
from logging import getLogger

from schematics import Model
from schematics.types import (
    StringType,
    ModelType,
    ListType,
    IntType,
    BooleanType,
    TimestampType
)

from selene.api import PublicEndpoint
from selene.data.device import ManifestSkill, DeviceSkillRepository
from selene.data.skill import SkillRepository


class SkillManifestReconciler(object):
    def __init__(self, db, device_manifest, db_manifest):
        """
        Initialize the device.

        Args:
            self: (todo): write your description
            db: (todo): write your description
            device_manifest: (todo): write your description
            db_manifest: (dict): write your description
        """
        self.db = db
        self.skill_manifest_repo = DeviceSkillRepository(db)
        self.skill_repo = SkillRepository(self.db)
        self.device_manifest = {sm.skill_gid: sm for sm in device_manifest}
        self.db_manifest = {ds.skill_gid: ds for ds in db_manifest}
        self.device_manifest_global_ids = {
            gid for gid in self.device_manifest.keys()
        }
        self.db_manifest_global_ids = {gid for gid in self.db_manifest}

    def reconcile(self):
        """Compare the manifest sent by the device to that on the database."""
        self._update_skills()
        self._remove_skills()
        self._add_skills()

    def _update_skills(self):
        """
        Update the manifest.

        Args:
            self: (todo): write your description
        """
        common_global_ids = self.device_manifest_global_ids.intersection(
            self.db_manifest_global_ids
        )
        for gid in common_global_ids:
            if self.device_manifest[gid] == self.db_manifest[gid]:
                self.skill_manifest_repo.update_manifest_skill(
                    self.device_manifest[gid]
                )

    def _remove_skills(self):
        """
        Removes differences from the manifest.

        Args:
            self: (todo): write your description
        """
        skills_to_remove = self.db_manifest_global_ids.difference(
            self.device_manifest_global_ids
        )
        for gid in skills_to_remove:
            manifest_skill = self.db_manifest[gid]
            self.skill_manifest_repo.remove_manifest_skill(manifest_skill)
            if manifest_skill.device_id in gid:
                self.skill_repo.remove_by_gid(gid)

    def _add_skills(self):
        """
        Add differences to the manifest.

        Args:
            self: (todo): write your description
        """
        skills_to_add = self.device_manifest_global_ids.difference(
            self.db_manifest_global_ids
        )

        for gid in skills_to_add:
            skill_id = self.skill_repo.ensure_skill_exists(gid)
            self.device_manifest[gid].skill_id = skill_id
            self.skill_manifest_repo.add_manifest_skill(
                self.device_manifest[gid]
            )


class RequestManifestSkill(Model):
    name = StringType(required=True)
    origin = StringType(required=True)
    installation = StringType(required=True)
    failure_message = StringType(default='')
    status = StringType(required=True)
    beta = BooleanType(required=True)
    installed = TimestampType(required=True)
    updated = TimestampType(required=True)
    skill_gid = StringType(required=True)


class SkillManifestRequest(Model):
    blacklist = ListType(StringType)
    version = IntType()
    skills = ListType(ModelType(RequestManifestSkill, required=True))


_log = getLogger(__package__)


class DeviceSkillManifestEndpoint(PublicEndpoint):
    _device_skill_repo = None

    def __init__(self):
        """
        Initialize the device.

        Args:
            self: (todo): write your description
        """
        super(DeviceSkillManifestEndpoint, self).__init__()

    @property
    def device_skill_repo(self):
        """
        Return the skill skill skill skill.

        Args:
            self: (todo): write your description
        """
        if self._device_skill_repo is None:
            self._device_skill_repo = DeviceSkillRepository(self.db)

        return self._device_skill_repo

    def put(self, device_id):
        """
        Updates the device.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
        """
        self._authenticate(device_id)
        self._validate_put_request()
        self._update_skill_manifest(device_id)

        return '', HTTPStatus.OK

    def _validate_put_request(self):
        """
        Validate request data request.

        Args:
            self: (todo): write your description
        """
        request_data = SkillManifestRequest(self.request.json)
        request_data.validate()

    def _update_skill_manifest(self, device_id):
        """
        Updates the manifest.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
        """
        db_skill_manifest = self.device_skill_repo.get_skill_manifest_for_device(
            device_id
        )
        device_skill_manifest = []
        for manifest_skill in self.request.json['skills']:
            self._convert_manifest_timestamps(manifest_skill)
            device_skill_manifest.append(
                ManifestSkill(
                    device_id=device_id,
                    install_method=manifest_skill['origin'],
                    install_status=manifest_skill['installation'],
                    install_failure_reason=manifest_skill.get('failure_message'),
                    install_ts=manifest_skill['installed'],
                    skill_gid=manifest_skill['skill_gid'],
                    update_ts=manifest_skill['updated']
                )
            )
        reconciler = SkillManifestReconciler(
            self.db,
            device_skill_manifest,
            db_skill_manifest
        )
        reconciler.reconcile()

    @staticmethod
    def _convert_manifest_timestamps(manifest_skill):
        """
        Convert manifest to manifest

        Args:
            manifest_skill: (str): write your description
        """
        for key in ('installed', 'updated'):
            value = manifest_skill[key]
            if value:
                manifest_skill[key] = datetime.fromtimestamp(value)
            else:
                manifest_skill[key] = None
