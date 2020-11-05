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

import os

import requests

from selene.api import PublicEndpoint


class OauthCallbackEndpoint(PublicEndpoint):

    def __init__(self):
        """
        Initialize the oauth2 client.

        Args:
            self: (todo): write your description
        """
        super(OauthCallbackEndpoint, self).__init__()
        self.oauth_service_host = os.environ['OAUTH_BASE_URL']

    def get(self):
        """
        Returns the request the oauth2 request

        Args:
            self: (todo): write your description
        """
        params = dict(self.request.args)
        url = self.oauth_service_host + '/auth/callback'
        response = requests.get(url, params=params)
        return response.text, response.status_code
