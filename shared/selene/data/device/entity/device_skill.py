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

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ManifestSkill(object):
    device_id: str
    install_method: str
    install_status: str
    skill_gid: str
    install_failure_reason: str = None
    install_ts: datetime = None
    skill_id: str = None
    update_ts: datetime = None
    id: str = None


@dataclass
class AccountSkillSettings(object):
    install_method: str
    skill_id: str
    device_ids: List[str] = None
    settings_values: dict = None
    settings_display_id: str = None


@dataclass
class DeviceSkillSettings(object):
    skill_id: str
    skill_gid: str
    settings_values: dict = None
    settings_display_id: str = None
