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


class PairingCodeEndpoint(SeleneEndpoint):
    def __init__(self):
        """
        Initialize the application.

        Args:
            self: (todo): write your description
        """
        super(PairingCodeEndpoint, self).__init__()
        self.cache = self.config['SELENE_CACHE']

    def get(self, pairing_code):
        """
        Returns a dict with the keys ) pairs.

        Args:
            self: (todo): write your description
            pairing_code: (str): write your description
        """
        self._authenticate()
        pairing_code_is_valid = self._get_pairing_data(pairing_code)

        return dict(isValid=pairing_code_is_valid), HTTPStatus.OK

    def _get_pairing_data(self, pairing_code: str) -> bool:
        """Checking if there's one pairing session for the pairing code."""
        pairing_code_is_valid = False
        cache_key = 'pairing.code:' + pairing_code
        pairing_cache = self.cache.get(cache_key)
        if pairing_cache is not None:
            pairing_code_is_valid = True

        return pairing_code_is_valid
