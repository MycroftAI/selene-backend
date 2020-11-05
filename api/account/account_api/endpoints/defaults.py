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

from flask import json
from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.data.device import DefaultsRepository


class DefaultsRequest(Model):
    city = StringType()
    country = StringType()
    region = StringType()
    timezone = StringType()
    voice = StringType()
    wake_word = StringType()


class AccountDefaultsEndpoint(SeleneEndpoint):
    def __init__(self):
        """
        Initialize the default values.

        Args:
            self: (todo): write your description
        """
        super(AccountDefaultsEndpoint, self).__init__()
        self.defaults = None

    def get(self):
        """
        Returns a response.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        self._get_defaults()
        if self.defaults is None:
            response_data = ''
            response_code = HTTPStatus.NO_CONTENT
        else:
            response_data = self.defaults
            response_code = HTTPStatus.OK

        return response_data, response_code

    def _get_defaults(self):
        """
        Gets the default repository

        Args:
            self: (todo): write your description
        """
        default_repository = DefaultsRepository(self.db, self.account.id)
        self.defaults = default_repository.get_account_defaults()

    def post(self):
        """
        Perform post request.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        defaults = self._validate_request()
        self._upsert_defaults(defaults)

        return '', HTTPStatus.NO_CONTENT

    def patch(self):
        """
        Patch the request.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        defaults = self._validate_request()
        self._upsert_defaults(defaults)

        return '', HTTPStatus.NO_CONTENT

    def _validate_request(self):
        """
        Validate the request.

        Args:
            self: (todo): write your description
        """
        request_data = json.loads(self.request.data)
        defaults = DefaultsRequest()
        defaults.city = request_data.get('city')
        defaults.country = request_data.get('country')
        defaults.region = request_data.get('region')
        defaults.timezone = request_data.get('timezone')
        defaults.voice = request_data['voice']
        defaults.wake_word = request_data['wakeWord']
        defaults.validate()

        return defaults

    def _upsert_defaults(self, defaults):
        """
        Update the default repository : param default repository.

        Args:
            self: (todo): write your description
            defaults: (todo): write your description
        """
        defaults_repository = DefaultsRepository(self.db, self.account.id)
        defaults_repository.upsert(defaults.to_native())
