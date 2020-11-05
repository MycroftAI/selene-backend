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
from selene.util.auth import AuthenticationToken


class ValidateTokenEndpoint(SeleneEndpoint):
    def post(self):
        """
        Validate the token.

        Args:
            self: (todo): write your description
        """
        response_data = self._validate_token()
        return response_data, HTTPStatus.OK

    def _validate_token(self):
        """
        Validate an access token.

        Args:
            self: (todo): write your description
        """
        auth_token = AuthenticationToken(
            self.config['RESET_SECRET'],
            duration=0
        )
        auth_token.jwt = self.request.json['token']
        auth_token.validate()

        return dict(
            account_id=auth_token.account_id,
            token_expired=auth_token.is_expired,
            token_invalid=not auth_token.is_valid
        )
