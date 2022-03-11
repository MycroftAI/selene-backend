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

from binascii import a2b_base64
from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.auth import (
    get_facebook_account_email,
    get_github_account_email,
    get_google_account_email,
)


class ValidateEmailEndpoint(SeleneEndpoint):
    def get(self):
        return_data = dict(accountExists=False, noFederatedEmail=False)
        if self.request.args["token"]:
            email_address = self._get_email_address()
            if self.request.args["platform"] != "Internal" and not email_address:
                return_data.update(noFederatedEmail=True)
            account_repository = AccountRepository(self.db)
            account = account_repository.get_account_by_email(email_address)
            if account is None:
                return_data.update(accountExists=False)

        return return_data, HTTPStatus.OK

    def _get_email_address(self):
        if self.request.args["platform"] == "Google":
            email_address = get_google_account_email(self.request.args["token"])
        elif self.request.args["platform"] == "Facebook":
            email_address = get_facebook_account_email(self.request.args["token"])
        elif self.request.args["platform"] == "GitHub":
            email_address = get_github_account_email(self.request.args["token"])
        else:
            coded_email = self.request.args["token"]
            email_address = a2b_base64(coded_email).decode()

        return email_address
