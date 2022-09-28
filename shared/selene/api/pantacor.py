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
import logging
import requests
from os import environ

from selene.data.device import PantacorConfig

_log = logging.getLogger(__name__)


class PantacorError(Exception):
    """Custom exception for unexpected occurrences in a Pantacor APi calls."""


def _get_release_channels():
    """Use the API to get the list of available software release channels."""
    release_channels = {}
    response_data = _call_pantacor_api("GET", endpoint="channels")
    for channel in response_data["items"]:
        release_channels[channel["id"]] = channel["name"]

    return release_channels


def get_pantacor_device(pantacor_device_id: str) -> PantacorConfig:
    """Use the API to search for a device based on the pairing code.

    :param pantacor_device_id: six character code used to pair a device to Selene
    :raises PantacorError: raised when multiple devices match a pairing code
    """
    _log.info(
        f"Requesting device information for pantacor device ID {pantacor_device_id}"
    )
    release_channels = _get_release_channels()
    response_data = _call_pantacor_api("GET", endpoint=f"devices/{pantacor_device_id}")
    if not response_data:
        raise PantacorError("Pantacor device ID not found.")
    ip_address = None
    claimed = False
    for label in response_data["labels"]:
        if label.startswith("device-meta"):
            label = label.replace("device-meta/", "")
            key, value = label.split("=")
            if key == "interfaces.eth0.ipv4.0":
                ip_address = value
            if key == "interfaces.wlan0.ipv4.0" and ip_address is None:
                ip_address = value
            elif key == "pantahub.claimed":
                claimed = value == "1"

    return PantacorConfig(
        pantacor_id=pantacor_device_id,
        ip_address=ip_address,
        release_channel=release_channels[response_data["channel_id"]],
        auto_update=response_data["update_policy"] == "auto",
        claimed=claimed,
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


def _change_pantacor_update_policy(device_id: str, auto_update: bool):
    """Use the API to change the update policy of the device.

    :param device_id: Pantacor device ID
    :param auto_update: the new value of the attribute
    """
    update_policy = "auto" if auto_update else "manual"
    data = dict(update_policy=update_policy)
    _call_pantacor_api("PATCH", endpoint="devices/" + device_id, data=data)


def _change_pantacor_release_channel(device_id: str, release_channel: str):
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


def _change_pantacor_ssh_key(device_id: str, ssh_key: str):
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
        timeout=5,
    )

    if response.ok:
        response_data = json.loads(response.content.decode())
    else:
        raise PantacorError(
            f"{method} {url} failed.  Status code: {response.status_code}  "
            f"Content: {response.content.decode()}"
        )

    return response_data


def update_pantacor_config(old_config: dict, new_config: dict):
    """Make calls to the Pantacor API to update any values that have changed.

    :param old_config: the config values before the update.
    :param new_config: the new config values (which may be the same as the old values)
    """
    for config_name, new_value in new_config.items():
        old_value = old_config[config_name]
        if old_value != new_value:
            if config_name == "auto_update":
                _change_pantacor_update_policy(old_config["pantacor_id"], new_value)
            elif config_name == "release_channel":
                _change_pantacor_release_channel(old_config["pantacor_id"], new_value)
            elif config_name == "ssh_public_key":
                _change_pantacor_ssh_key(old_config["pantacor_id"], new_value)
