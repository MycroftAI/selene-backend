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

from dataclasses import asdict
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.api.etag import ETagManager
from selene.data.device import AccountPreferences, PreferenceRepository


class PreferencesRequest(Model):
    date_format = StringType(
        required=True,
        choices=['DD/MM/YYYY', 'MM/DD/YYYY']
    )
    measurement_system = StringType(
        required=True,
        choices=['Imperial', 'Metric']
    )
    time_format = StringType(required=True, choices=['12 Hour', '24 Hour'])


class PreferencesEndpoint(SeleneEndpoint):
    def __init__(self):
        """
        Initialize the manager.

        Args:
            self: (todo): write your description
        """
        super(PreferencesEndpoint, self).__init__()
        self.preferences = None
        self.cache = self.config['SELENE_CACHE']
        self.etag_manager: ETagManager = ETagManager(self.cache, self.config)

    def get(self):
        """
        Fet preferences.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        self._get_preferences()
        if self.preferences is None:
            response_data = ''
            response_code = HTTPStatus.NO_CONTENT
        else:
            response_data = asdict(self.preferences)
            response_code = HTTPStatus.OK

        return response_data, response_code

    def _get_preferences(self):
        """
        Gets preferences for the preferences

        Args:
            self: (todo): write your description
        """
        preference_repository = PreferenceRepository(self.db, self.account.id)
        self.preferences = preference_repository.get_account_preferences()

    def post(self):
        """
        Perform post request.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        self._validate_request()
        self._upsert_preferences()
        self.etag_manager.expire_device_setting_etag_by_account_id(self.account.id)
        return '', HTTPStatus.NO_CONTENT

    def patch(self):
        """
        Patch the device authentication.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        self._validate_request()
        self._upsert_preferences()
        self.etag_manager.expire_device_setting_etag_by_account_id(self.account.id)
        return '', HTTPStatus.NO_CONTENT

    def _validate_request(self):
        """
        Validate the preferences.

        Args:
            self: (todo): write your description
        """
        self.preferences = PreferencesRequest()
        self.preferences.date_format = self.request.json['dateFormat']
        self.preferences.measurement_system = (
            self.request.json['measurementSystem']
        )
        self.preferences.time_format = self.request.json['timeFormat']
        self.preferences.validate()

    def _upsert_preferences(self):
        """
        Preference preferences.

        Args:
            self: (todo): write your description
        """
        preferences_repository = PreferenceRepository(self.db, self.account.id)
        preferences = AccountPreferences(**self.preferences.to_native())
        preferences_repository.upsert(preferences)
