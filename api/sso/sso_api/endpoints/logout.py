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

"""Log a user out of Mycroft web sites"""

from http import HTTPStatus
from logging import getLogger

from selene.api import SeleneEndpoint

_log = getLogger(__package__)


class LogoutEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        self._logout()

        return self.response

    def _logout(self):
        """Delete tokens from database and expire the token cookies.

        An absence of tokens will force the user to re-authenticate next time
        they visit the site.
        """
        self._generate_tokens()
        self._set_token_cookies(expire=True)

        self.response = ('', HTTPStatus.NO_CONTENT)
