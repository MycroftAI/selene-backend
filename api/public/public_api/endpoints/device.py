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
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.api import device_etag_key
from selene.data.device import DeviceRepository


class UpdateDevice(Model):
    coreVersion = StringType(default='unknown')
    platform = StringType(default='unknown')
    platform_build = StringType()
    enclosureVersion = StringType(default='unknown')


class DeviceEndpoint(PublicEndpoint):
    """Return the device entity using the device_id"""
    def __init__(self):
        super(DeviceEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        self._validate_etag(device_etag_key(device_id))
        device = DeviceRepository(self.db).get_device_by_id(device_id)

        if device is not None:
            response_data = dict(
                uuid=device.id,
                name=device.name,
                description=device.placement,
                coreVersion=device.core_version,
                enclosureVersion=device.enclosure_version,
                platform=device.platform,
                user=dict(uuid=device.account_id)
            )
            response = response_data, HTTPStatus.OK

            self._add_etag(device_etag_key(device_id))
        else:
            response = '', HTTPStatus.NO_CONTENT

        return response

    def patch(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        update_device = UpdateDevice(payload)
        update_device.validate()
        updates = dict(
            platform=payload.get('platform') or 'unknown',
            enclosure_version=payload.get('enclosureVersion') or 'unknown',
            core_version=payload.get('coreVersion') or 'unknown'
        )
        DeviceRepository(self.db).update_device_from_core(device_id, updates)

        return '', HTTPStatus.OK
