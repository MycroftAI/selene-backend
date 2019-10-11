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

import json
from datetime import datetime

from selene.data.device import DeviceSkillRepository, ManifestSkill


def add_device_skill(db, device_id, skill):
    manifest_skill = ManifestSkill(
        device_id=device_id,
        install_method='test_install_method',
        install_status='test_install_status',
        skill_id=skill.id,
        skill_gid=skill.skill_gid,
        install_ts=datetime.utcnow(),
        update_ts=datetime.utcnow()
    )
    device_skill_repo = DeviceSkillRepository(db)
    manifest_skill.id = device_skill_repo.add_manifest_skill(manifest_skill)

    return manifest_skill


def add_device_skill_settings(db, device_id, settings_display, settings_values):
    device_skill_repo = DeviceSkillRepository(db)
    device_skill_repo.upsert_device_skill_settings(
        [device_id],
        settings_display,
        settings_values
    )


def remove_device_skill(db, manifest_skill):
    device_skill_repo = DeviceSkillRepository(db)
    device_skill_repo.remove_manifest_skill(manifest_skill)
