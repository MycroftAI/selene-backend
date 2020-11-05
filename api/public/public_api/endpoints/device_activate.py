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

"""Endpoint to activate a device and finish the pairing process.

A device will call this endpoint every 10 seconds to determine if the user
has completed the device activation process on home.mycroft.ai.  The account
API will set a Redis entry with the a key of "pairing.token" and a value of
the pairing token generated in the pairing code endpoint.  The device passes
the same token in the request body.  When a match is found, the activation
is complete.
"""
import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.api import generate_device_login
from selene.data.device import DeviceRepository
from selene.util.cache import DEVICE_PAIRING_TOKEN_KEY


class ActivationRequest(Model):
    token = StringType(required=True)
    state = StringType(required=True)
    platform = StringType(default='unknown')
    coreVersion = StringType(default='unknown')
    enclosureVersion = StringType(default='unknown')
    platform_build = StringType()


class DeviceActivateEndpoint(PublicEndpoint):
    def post(self):
        """
        Perform post request.

        Args:
            self: (todo): write your description
        """
        activation_request = self._validate_request()
        pairing_session = self._get_pairing_session()
        if pairing_session is not None:
            device_id = pairing_session['uuid']
            self._activate(device_id, activation_request)
            response = (
                generate_device_login(device_id, self.cache),
                HTTPStatus.OK
            )
        else:
            response = '', HTTPStatus.NOT_FOUND
        return response

    def _validate_request(self):
        """
        Validate the activation request.

        Args:
            self: (todo): write your description
        """
        activation_request = ActivationRequest(self.request.json)
        activation_request.validate()

        return activation_request

    def _get_pairing_session(self):
        """Get the pairing session from the cache.

        The request must have same state value as that stored in the
        pairing session.
        """
        pairing_session_token = self.request.json['token']
        pairing_session_key = DEVICE_PAIRING_TOKEN_KEY.format(
            pairing_token=pairing_session_token
        )
        pairing_session = self.cache.get(pairing_session_key)
        if pairing_session:
            pairing_session = json.loads(pairing_session)
            if self.request.json['state'] == pairing_session['state']:
                self.cache.delete(pairing_session_key)
                return pairing_session

    def _activate(self, device_id: str, activation_request: ActivationRequest):
        """Updates the core version, platform and enclosure_version columns"""
        updates = dict(
            platform=str(activation_request.platform),
            enclosure_version=str(activation_request.enclosureVersion),
            core_version=str(activation_request.coreVersion)
        )
        DeviceRepository(self.db).update_device_from_core(device_id, updates)
