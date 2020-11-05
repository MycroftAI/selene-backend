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

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository


class StripeWebHookEndpoint(PublicEndpoint):

    def __init__(self):
        """
        Initialize the logger.

        Args:
            self: (todo): write your description
        """
        super(StripeWebHookEndpoint, self).__init__()

    def post(self):
        """
        Handle post request

        Args:
            self: (todo): write your description
        """
        event = json.loads(self.request.data)
        type = event.get('type')
        if type == 'customer.subscription.deleted':
            customer = event['data']['object']['customer']
            AccountRepository(self.db).end_active_membership(customer)
        return '', HTTPStatus.OK
