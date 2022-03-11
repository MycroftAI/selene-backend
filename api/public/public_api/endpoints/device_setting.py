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

from http import HTTPStatus

from selene.api import PublicEndpoint, device_setting_etag_key
from selene.data.device import SettingRepository


class DeviceSettingEndpoint(PublicEndpoint):
    """Return the device's settings for the API v1 model"""

    def __init__(self):
        super(DeviceSettingEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        self._validate_etag(device_setting_etag_key(device_id))
        setting = SettingRepository(self.db).get_device_settings(device_id)
        if setting is not None:
            response = (setting, HTTPStatus.OK)
            self._add_etag(device_setting_etag_key(device_id))
        else:
            response = ("", HTTPStatus.NO_CONTENT)
        return response
