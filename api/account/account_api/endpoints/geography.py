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
from selene.data.device import GeographyRepository


class GeographyEndpoint(SeleneEndpoint):
    def get(self):
        """
        Returns the authentication data.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        """
        Build a response data dictionary from the data.

        Args:
            self: (todo): write your description
        """
        geography_repository = GeographyRepository(self.db, self.account.id)
        geographies = geography_repository.get_account_geographies()

        response_data = []
        for geography in geographies:
            response_data.append(
                dict(id=geography.id, name=geography.country, user_defined=True)
            )

        return response_data
