# Mycroft Server - Backend
# Copyright (C) 2022 Mycroft AI Inc
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
from http import HTTPStatus
from logging import getLogger

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.api.pantacor import get_pantacor_device, PantacorError
from selene.data.device import DeviceRepository

_log = getLogger(__package__)


class PantacorSyncRequest(Model):
    """Data model of the fields in the request."""

    mycroft_device_id = StringType(required=True)
    pantacor_device_id = StringType(required=True)


class DevicePantacorEndpoint(PublicEndpoint):
    """API endpoint for devices that use Pantacor for deployments.

    Retrieves Pantacor configuration values, such as "auto update" from the
    Pantacor Fleet API and adds the config to the device.pantacor table in the
    database.  The data on this table allows users to view and edit the config
    values in the Selene UI.  For this endpoint to be successful, the Pantacor Device
    ID must be recognized by Pantacor and the device must be "claimed" by Pantacor.
    """

    def post(self):
        """Process a HTTP POST request."""
        self._validate_request()
        pantacor_config = self._get_config_from_pantacor()
        if pantacor_config is None:
            response = "Pantacor Device ID not found", HTTPStatus.NOT_FOUND
        elif not pantacor_config.claimed:
            response = (
                "Device not yet claimed by Pantacor",
                HTTPStatus.PRECONDITION_REQUIRED,
            )
        else:
            self._add_pantacor_config_to_db(pantacor_config)
            response = "", HTTPStatus.OK

        return response

    def _validate_request(self):
        """Validate the contents of the API request against the data model."""
        # TODO: remove this hack when mycroft-core mark-2 branch is merged into dev
        activation_request = PantacorSyncRequest(self.request.json)
        activation_request.validate()

    def _get_config_from_pantacor(self):
        """Attempts to get the Pantacor config values from their Fleet API."""
        pantacor_config = None
        try:
            pantacor_config = get_pantacor_device(
                self.request.json["pantacor_device_id"]
            )
        except PantacorError:
            _log.exception("Pantacor device ID not found on PantaHub")

        return pantacor_config

    def _add_pantacor_config_to_db(self, pantacor_config):
        """Adds the software update configs to the database."""
        device_repository = DeviceRepository(self.db)
        device_repository.add_pantacor_config(
            self.request.json["mycroft_device_id"], pantacor_config
        )
