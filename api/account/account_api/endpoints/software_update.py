# Mycroft Server - Backend
# Copyright (C) 2021 Mycroft AI Inc
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
"""Endpoint to process a user's request to apply an software update on their device."""
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.api.pantacor import apply_pantacor_update


class SoftwareUpdateRequest(Model):
    """Schematic for a request to update software on a device."""

    deployment_id = StringType(required=True)


class SoftwareUpdateEndpoint(SeleneEndpoint):
    """Send a request to Pantacor to update a device."""

    def patch(self):
        """Handle a HTTP PATCH request."""
        self._authenticate()
        self._validate_request()
        apply_pantacor_update(self.request.json["deploymentId"])
        return "", HTTPStatus.NO_CONTENT

    def _validate_request(self):
        """Validate the contents of the PATCH request."""
        request_validator = SoftwareUpdateRequest()
        request_validator.deployment_id = self.request.json["deploymentId"]
        request_validator.validate()
