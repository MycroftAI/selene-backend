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

from selene.data.device import PantacorConfig


class PantacorError(Exception):
    """Custom exception for unexpected occurrences in a Pantacor APi calls."""


def _get_release_channels():
    """Use the API to get the list of available software release channels."""
    release_channels = {}
    response_data = _call_pantacor_api("GET", endpoint="channels")
    for channel in response_data["items"]:
        release_channels[channel["id"]] = channel["name"]

    return release_channels


def get_pantacor_device(pairing_code: str) -> PantacorConfig:
    """Use the API to search for a device based on the pairing code.

    :param pairing_code: six character code used to pair a device to Selene
    :raises PantacorError: raised when multiple devices match a pairing code
    """
    params = dict(labels="device-meta/mycroft.pairing_code=" + pairing_code)
    release_channels = _get_release_channels()
    response_data = _call_pantacor_api("GET", endpoint="devices", params=params)
    if len(response_data["items"]) > 1:
        raise PantacorError("Multiple devices returned for a pairing code")
    device = response_data["items"][0]
    ip_address = None
    for label in device["labels"]:
        if label.startswith("device-meta"):
            key, value = label.split("=")
            if key == "device-meta/interfaces.wlan0.ipv4.0":
                ip_address = value
                break

    return PantacorConfig(
        pantacor_id=device["id"],
        ip_address=ip_address,
        release_channel=release_channels[device["channel_id"]],
        auto_update=device["update_policy"] == "auto",
    )


def get_pantacor_pending_deployment(device_id: str):
    """Use the API to search for a device based on the pairing code.

    :param device_id: Pantacor device ID
    :raises PantacorError: raised when multiple devices match a pairing code
    """
    update_id = None
    params = dict(device_id=device_id, fields="-step")
    response_data = _call_pantacor_api(
        "GET", endpoint="deployment-actions/pending", params=params
    )
    if response_data["items"]:
        pending_update = response_data["items"][0]
        update_id = pending_update["id"]

    return update_id


def apply_pantacor_update(deployment_id: str):
    """Use the API to change the update policy of the device.

    :param deployment_id: identifier of a Pantacor deployment to a device.
    """
    endpoint = f"deployment-actions/{deployment_id}/play"
    _call_pantacor_api("PATCH", endpoint=endpoint)


def change_pantacor_update_policy(device_id: str, auto_update: bool):
    """Use the API to change the update policy of the device.

    :param device_id: Pantacor device ID
    :param auto_update: the new value of the attribute
    """
    update_policy = "auto" if auto_update else "manual"
    data = dict(update_policy=update_policy)
    _call_pantacor_api("PATCH", endpoint="devices/" + device_id, data=data)


def change_pantacor_release_channel(device_id: str, release_channel: str):
    """Use the API to change the release channel the device is subscribed to.

    We know the names of the release channels, but not their IDs.  Make an extra
    API call to get the list of valid release channels so we can pass the ID
    in the PATCH request.

    :param device_id: Pantacor device ID
    :param release_channel: name of the Pantacor release channel
    :raises PantacorError: raised if supplied channel name is not in the Pantacor list
    """
    release_channels = _get_release_channels()
    new_channel_id = None
    for key, value in release_channels.items():
        if release_channel == value:
            new_channel_id = key
    if new_channel_id is None:
        raise PantacorError("Could not find release channel " + release_channel)
    data = dict(channel_id=new_channel_id)
    _call_pantacor_api("PATCH", endpoint="devices/" + device_id, data=data)


def change_pantacor_ssh_key(device_id: str, ssh_key: str):
    """Use the API to change the SSH key used to login to the device remotely.

    :param device_id: Pantacor device ID
    :param ssh_key: public SSH key of a computer used to log into a device
    :raises PantacorError: raised if supplied channel name is not in the Pantacor list
    """
    data = {"pvr-sdk.authorized_keys": ssh_key}
    endpoint = "devices/" + device_id + "/user-meta"
    _call_pantacor_api("PATCH", endpoint=endpoint, data=data)


def _call_pantacor_api(method: str, endpoint: str, **kwargs):
    """Issue a request to the Pantacor API.

    :param method: HTTP request method (i.e. GET, PUT, etc.)
    :param endpoint: portion of URL indicating which endpoint to hit.
    """
    access_token = environ["PANTACOR_API_TOKEN"]
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
    }
    url = environ["PANTACOR_API_BASE_URL"] + endpoint
    response = requests.request(
        method,
        url,
        params=kwargs.get("params"),
        headers=headers,
        data=json.dumps(kwargs.get("data")),
    )

    if response.ok:
        response_data = json.loads(response.content.decode())
    else:
        raise PantacorError(
            f"{method} {url} failed.  Status code: {response.status_code}  "
            f"Content: {response.content.decode()}"
        )

    return response_data
