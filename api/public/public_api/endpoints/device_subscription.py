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
from selene.data.account import AccountRepository


class DeviceSubscriptionEndpoint(PublicEndpoint):
    def __init__(self):
        """
        Initialize the device.

        Args:
            self: (todo): write your description
        """
        super(DeviceSubscriptionEndpoint, self).__init__()

    def get(self, device_id):
        """
        Fetches account.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
        """
        self._authenticate(device_id)
        account = AccountRepository(self.db).get_account_by_device_id(device_id)
        if account:
            membership = account.membership
            response = (
                {'@type': membership.type if membership is not None else 'free'},
                HTTPStatus.OK
            )
        else:
            response = '', HTTPStatus.NO_CONTENT

        return response
