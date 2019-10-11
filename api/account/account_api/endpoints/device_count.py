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
from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository


class DeviceCountEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        device_count = self._get_devices()

        return dict(deviceCount=device_count), HTTPStatus.OK

    def _get_devices(self):
        device_repository = DeviceRepository(self.db)
        device_count = device_repository.get_account_device_count(
            self.account.id
        )

        return device_count
