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

from selene.api import PublicEndpoint
from selene.api.etag import device_location_etag_key
from selene.data.device import GeographyRepository


class DeviceLocationEndpoint(PublicEndpoint):

    def __init__(self):
        super(DeviceLocationEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        self._validate_etag(device_location_etag_key(device_id))
        location = GeographyRepository(self.db, None).get_location_by_device_id(device_id)
        if location:
            response = (location, HTTPStatus.OK)
            self._add_etag(device_location_etag_key(device_id))
        else:
            response = ('', HTTPStatus.NOT_FOUND)
        return response
