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
"""Interface with the Pantacor API for devices with software managed by them."""
import json
import requests
from os import environ

BASE_URL = "https://stage.fleet.pantacor.com/api/v1/"


def get_pantacor_device_id(pairing_code: str):
    """Call the Pantacor API to search for a device based on the pairing code."""
    device_id = None
    url = BASE_URL + "devices"
    params = dict(labels="device-meta/mycroft.pairing_code=" + pairing_code)
    access_token = environ["PANTACOR_TOKEN"]
    headers = dict(Authorization="Bearer " + access_token)
    response = requests.get(url, params=params, headers=headers)

    if response.ok:
        response_data = json.loads(response.content.decode())
        device = response_data["items"][0]
        device_id = device["id"]

    return device_id
