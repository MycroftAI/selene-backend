#  Mycroft Server - Backend
#  Copyright (c) 2022 Mycroft AI Inc
#  SPDX-License-Identifier: 	AGPL-3.0-or-later
#  #
#  This file is part of the Mycroft Server.
#  #
#  The Mycroft Server is free software: you can redistribute it and/or
#  modify it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  #
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#  #
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
#
"""Defines the password change endpoint for the account API."""

from selene.api.endpoints import PasswordChangeEndpoint as CommonPasswordChangeEndpoint


class PasswordChangeEndpoint(CommonPasswordChangeEndpoint):
    """Adds authentication to the common password changing endpoint."""

    @property
    def account_id(self):
        """Returns the account passed to the endpoint in the PUT request"""
        return self.request.json["accountId"]

    def _authenticate(self):
        """Skips authentication because user is not logged in when this is called."""
