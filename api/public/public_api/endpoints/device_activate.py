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
from logging import getLogger

from schematics import Model
from schematics.types import StringType

from selene.api import generate_device_login, PublicEndpoint
from selene.api.pantacor import get_pantacor_device, PantacorError
from selene.data.device import DeviceRepository
from selene.util.cache import DEVICE_PAIRING_TOKEN_KEY

_log = getLogger(__package__)


class ActivationRequest(Model):
    """Data model of the fields in the request."""

    token = StringType(required=True)
    state = StringType(required=True)
    platform = StringType(default="unknown")
    core_version = StringType(default="unknown")
    enclosure_version = StringType(default="unknown")
    platform_build = StringType()
    pantacor_device_id = StringType()


class DeviceActivateEndpoint(PublicEndpoint):
    """API endpoint for activating a device, the last step in device pairing."""

    _device_repository = None

    @property
    def device_repository(self):
        """Lazily load an instance of the device repository"""
        if self._device_repository is None:
            self._device_repository = DeviceRepository(self.db)

        return self._device_repository

    def post(self):
        """Process a HTTP POST request."""
        activation_request = self._validate_request()
        pairing_session = self._get_pairing_session()
        if pairing_session is not None:
            device_id = pairing_session["uuid"]
            self._activate(device_id, activation_request)
            response = (generate_device_login(device_id, self.cache), HTTPStatus.OK)
        else:
            response = "", HTTPStatus.NOT_FOUND

        return response

    def _validate_request(self) -> dict:
        """Validate the contents of the API request against the data model."""
        # TODO: remove this hack when mycroft-core mark-2 branch is merged into dev
        if "coreVersion" in self.request.json:
            self.request.json["core_version"] = self.request.json["coreVersion"]
            del self.request.json["coreVersion"]
        if "enclosureVersion" in self.request.json:
            self.request.json["enclosure_version"] = self.request.json[
                "enclosureVersion"
            ]
            del self.request.json["enclosureVersion"]
        activation_request = ActivationRequest(self.request.json)
        activation_request.validate()

        return activation_request.to_native()

    def _get_pairing_session(self):
        """Get the pairing session from the cache.

        The request must have same state value as that stored in the
        pairing session.
        """
        pairing_session_token = self.request.json["token"]
        pairing_session_key = DEVICE_PAIRING_TOKEN_KEY.format(
            pairing_token=pairing_session_token
        )
        pairing_session = self.cache.get(pairing_session_key)
        if pairing_session:
            pairing_session = json.loads(pairing_session)
            if self.request.json["state"] == pairing_session["state"]:
                self.cache.delete(pairing_session_key)

        return pairing_session

    def _activate(self, device_id: str, activation_request: dict):
        """Updates the core version, platform and enclosure_version columns

        :param device_id: internal identifier of the device
        :param activation_request: validated request data
        """
        updates = dict(
            platform=str(activation_request["platform"]),
            enclosure_version=str(activation_request["enclosure_version"]),
            core_version=str(activation_request["core_version"]),
        )
        self.device_repository.update_device_from_core(device_id, updates)

        if activation_request["pantacor_device_id"] is not None:
            self._add_pantacor_config(
                device_id, activation_request["pantacor_device_id"]
            )

    def _add_pantacor_config(self, device_id: str, pantacor_device_id: str):
        """The software updates are managed by Pantacor, get their ID and add to DB

        :param device_id: internal identifier of the device
        :param pantacor_device_id: identifier of a device on the Pantacor system
        """
        try:
            pantacor_config = get_pantacor_device(pantacor_device_id)
        except PantacorError:
            _log.exception("Pantacor device ID not found on PantaHub")
        else:
            self.device_repository.add_pantacor_config(device_id, pantacor_config)
