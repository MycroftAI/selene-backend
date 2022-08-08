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
"""Common parts of an endpoint to change a user's password."""
from binascii import a2b_base64
from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository


class PasswordChangeEndpoint(SeleneEndpoint):
    """Inherit this endpoint for password change endpoints."""

    def put(self):
        """Executes an HTTP PUT request."""
        self._authenticate()
        coded_password = self.request.json["password"]
        binary_password = a2b_base64(coded_password)
        password = binary_password.decode()
        acct_repository = AccountRepository(self.db)
        acct_repository.change_password(self.account_id, password)
        self._send_email()

        return "", HTTPStatus.NO_CONTENT

    @property
    def account_id(self):
        """Returns account ID, which can be obtained in different ways."""
        raise NotImplementedError

    def _send_email(self):
        """Override in subclass to send a password changed email."""
