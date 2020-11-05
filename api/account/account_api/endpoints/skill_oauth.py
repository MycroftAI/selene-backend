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

from selene.api import SeleneEndpoint


class SkillOauthEndpoint(SeleneEndpoint):
    def __init__(self):
        """
        Initialize the oauth2 session.

        Args:
            self: (todo): write your description
        """
        super(SkillOauthEndpoint, self).__init__()
        self.oauth_base_url = os.environ['OAUTH_BASE_URL']

    def get(self, oauth_id):
        """
        Returns the oauth by its id.

        Args:
            self: (todo): write your description
            oauth_id: (int): write your description
        """
        self._authenticate()
        return self._get_oauth_url(oauth_id)

    def _get_oauth_url(self, oauth_id):
        """
        Get oauth url for oauth. oauth.

        Args:
            self: (todo): write your description
            oauth_id: (str): write your description
        """
        url = '{base_url}/auth/{oauth_id}/auth_url?uuid={account_id}'.format(
            base_url=self.oauth_base_url,
            oauth_id=oauth_id,
            account_id=self.account.id
        )
        response = requests.get(url)
        return response.text, response.status_code
