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
"""Account API endpoint for retrieving and maintaining device information."""
from dataclasses import asdict
from datetime import datetime, timedelta
from http import HTTPStatus
from logging import getLogger
from typing import List

from flask import json
from schematics import Model
from schematics.exceptions import ValidationError
from schematics.types import BooleanType, StringType

from selene.api import SeleneEndpoint
from selene.api.etag import ETagManager
from selene.api.pantacor import (
    change_pantacor_release_channel,
    change_pantacor_ssh_key,
    change_pantacor_update_policy,
    get_pantacor_device,
    get_pantacor_pending_deployment,
)
from selene.api.public_endpoint import delete_device_login
from selene.data.device import Device, DeviceRepository, Geography, GeographyRepository
from selene.util.cache import (
    DEVICE_LAST_CONTACT_KEY,
    DEVICE_PAIRING_CODE_KEY,
    DEVICE_PAIRING_TOKEN_KEY,
    SeleneCache,
)

ONE_DAY = 86400
CONNECTED = "Connected"
DISCONNECTED = "Disconnected"
DORMANT = "Dormant"

_log = getLogger()


def validate_pairing_code(pairing_code):
    """Ensure the pairing code exists in the cache of valid pairing codes."""
    cache_key = DEVICE_PAIRING_CODE_KEY.format(pairing_code=pairing_code)
    cache = SeleneCache()
    pairing_cache = cache.get(cache_key)

    if pairing_cache is None:
        raise ValidationError("pairing code not found")


class UpdateDeviceRequest(Model):
    """Schematic for a request to update a device."""

    city = StringType(required=True)
    country = StringType(required=True)
    name = StringType(required=True)
    placement = StringType()
    region = StringType(required=True)
    timezone = StringType(required=True)
    wake_word = StringType(required=True)
    voice = StringType(required=True)
    auto_update = BooleanType()
    ssh_public_key = StringType()
    release_channel = StringType()


class NewDeviceRequest(UpdateDeviceRequest):
    """Schematic for a request to add a device."""

    pairing_code = StringType(required=True, validators=[validate_pairing_code])


class DeviceEndpoint(SeleneEndpoint):
    """Retrieve and maintain device information for the Account API"""

    _device_repository = None

    def __init__(self):
        super().__init__()
        self.devices = None
        self.cache = self.config["SELENE_CACHE"]
        self.etag_manager: ETagManager = ETagManager(self.cache, self.config)

    @property
    def device_repository(self):
        """Lazily instantiate the device repository."""
        if self._device_repository is None:
            self._device_repository = DeviceRepository(self.db)

        return self._device_repository

    def get(self, device_id: str):
        """Process an HTTP GET request."""
        self._authenticate()
        if device_id is None:
            response_data = self._get_devices()
        else:
            response_data = self._get_device(device_id)

        return response_data, HTTPStatus.OK

    def _get_devices(self) -> List[dict]:
        """Get a list of the devices belonging to the account in the request JWT

        :return: list of devices to be returned to the UI.
        """
        devices = self.device_repository.get_devices_by_account_id(self.account.id)
        response_data = []
        for device in devices:
            response_device = self._format_device_for_response(device)
            response_data.append(response_device)

        return response_data

    def _get_device(self, device_id: str) -> dict:
        """Get the device information for a specific device.

        :param device_id: Identifier of the device to retrieve
        :return: device information to return to the UI
        """
        device = self.device_repository.get_device_by_id(device_id)
        response_data = self._format_device_for_response(device)

        return response_data

    def _format_device_for_response(self, device: Device) -> dict:
        """Convert device object into a response object for this endpoint.

        :param device: the device data retrieved from the database.
        :return: device information formatted for the UI
        """
        pantacor_update_id = None
        if device.pantacor_config and not device.pantacor_config.auto_update:
            pantacor_update_id = get_pantacor_pending_deployment(
                device.pantacor_config.pantacor_id
            )
        last_contact_age = self._get_device_last_contact(device)
        device_status = self._determine_device_status(last_contact_age)
        if device_status == DISCONNECTED:
            disconnect_duration = self._determine_disconnect_duration(last_contact_age)
        else:
            disconnect_duration = None
        device.wake_word.name = device.wake_word.name.title()
        if device.pantacor_config.release_channel is not None:
            device.pantacor_config.release_channel = (
                device.pantacor_config.release_channel.title()
            )
        device_dict = asdict(device)
        device_dict["status"] = device_status
        device_dict["disconnect_duration"] = disconnect_duration
        device_dict["voice"] = device_dict.pop("text_to_speech")
        device_dict["pantacor_update_id"] = pantacor_update_id

        return device_dict

    def _get_device_last_contact(self, device: Device) -> timedelta:
        """Get the last time the device contacted the backend.

        The timestamp returned by this method will be used to determine if a
        device is active or not.

        The device table has a last contacted column but it is only updated
        daily via batch script.  The real-time values are kept in Redis.
        If the Redis query returns nothing, the device hasn't contacted the
        backend yet.  This could be because it was just activated. Give the
        device a couple of minutes to make that first call to the backend.

        :param device: the device data retrieved from the database.
        :return: the timestamp the device was last seen by Selene
        """
        last_contact_ts = self.cache.get(
            DEVICE_LAST_CONTACT_KEY.format(device_id=device.id)
        )
        if last_contact_ts is None:
            if device.last_contact_ts is None:
                last_contact_age = datetime.utcnow() - device.add_ts
            else:
                last_contact_age = datetime.utcnow() - device.last_contact_ts
        else:
            last_contact_ts = last_contact_ts.decode()
            last_contact_ts = datetime.strptime(last_contact_ts, "%Y-%m-%d %H:%M:%S.%f")
            last_contact_age = datetime.utcnow() - last_contact_ts

        return last_contact_age

    @staticmethod
    def _determine_device_status(last_contact_age: timedelta) -> str:
        """Derive device status from the last time device contacted servers.

        :param last_contact_age: amount of time since the device was last seen
        :return: the status of the device
        """
        if last_contact_age <= timedelta(seconds=120):
            device_status = CONNECTED
        elif timedelta(seconds=120) < last_contact_age < timedelta(days=30):
            device_status = DISCONNECTED
        else:
            device_status = DORMANT

        return device_status

    @staticmethod
    def _determine_disconnect_duration(last_contact_age: timedelta) -> str:
        """Derive device status from the last time device contacted servers.

        :param last_contact_age: amount of time since the device was last seen
        :return human readable amount of time since the device was last seen
        """
        disconnect_duration = "unknown"
        days, _ = divmod(last_contact_age, timedelta(days=1))
        if days:
            disconnect_duration = str(days) + " days"
        else:
            hours, remaining = divmod(last_contact_age, timedelta(hours=1))
            if hours:
                disconnect_duration = str(hours) + " hours"
            else:
                minutes, _ = divmod(remaining, timedelta(minutes=1))
                if minutes:
                    disconnect_duration = str(minutes) + " minutes"

        return disconnect_duration

    def post(self):
        """Handle a HTTP POST request."""
        self._authenticate()
        device = self._validate_request()
        device_id = self._pair_device(device)

        return device_id, HTTPStatus.OK

    def _validate_request(self) -> dict:
        """Validate the contents of the HTTP POST request."""
        request_data = json.loads(self.request.data)
        if self.request.method == "POST":
            device = NewDeviceRequest()
            device.pairing_code = request_data["pairingCode"]
        else:
            device = UpdateDeviceRequest()
        device.city = request_data["city"]
        device.country = request_data["country"]
        device.name = request_data["name"]
        device.placement = request_data["placement"]
        device.region = request_data["region"]
        device.timezone = request_data["timezone"]
        device.wake_word = request_data["wakeWord"].lower()
        device.voice = request_data["voice"]
        device.auto_update = request_data.get("autoUpdate")
        device.release_channel = request_data.get("releaseChannel")
        device.ssh_public_key = request_data.get("sshPublicKey")
        device.validate()

        return device.to_native()

    def _pair_device(self, device: dict) -> str:
        """Add the paired device to the database."""
        self.db.autocommit = False
        try:
            pairing_data = self._get_pairing_data(device["pairing_code"])
            device_id = self._add_device(device)
            pairing_data["uuid"] = device_id
            self.cache.delete(
                DEVICE_PAIRING_CODE_KEY.format(pairing_code=device["pairing_code"])
            )
            self._build_pairing_token(pairing_data)
            self._add_pantacor_config(device_id, pairing_data)
        except Exception:
            self.db.rollback()
            raise
        else:
            self.db.commit()

        return device_id

    def _get_pairing_data(self, pairing_code: str) -> dict:
        """Checking if there's one pairing session for the pairing code.

        :param pairing_code: the six character pairing code
        :return: the pairing code information from the Redis database
        """
        cache_key = DEVICE_PAIRING_CODE_KEY.format(pairing_code=pairing_code)
        pairing_cache = self.cache.get(cache_key)
        pairing_data = json.loads(pairing_cache)

        return pairing_data

    def _add_device(self, device: dict) -> str:
        """Creates a device and associate it to a pairing session.

        :param device: Schematic containing the request data
        :return: the database identifier of the new device
        """
        geography_id = self._ensure_geography_exists(device)
        device.update(geography_id=geography_id)
        device_id = self.device_repository.add(self.account.id, device)

        return device_id

    def _ensure_geography_exists(self, device: dict) -> str:
        """If the geography does not exist in the database, add it.

        :param device: attributes of the device
        :return: database identifier for the geography
        """
        geography = Geography(
            city=device["city"],
            country=device["country"],
            region=device["region"],
            time_zone=device["timezone"],
        )
        geography_repository = GeographyRepository(self.db, self.account.id)
        geography_id = geography_repository.get_geography_id(geography)
        if geography_id is None:
            geography_id = geography_repository.add(geography)

        return geography_id

    def _build_pairing_token(self, pairing_data: dict):
        """Add a pairing token to the Redis database.

        :param pairing_data: the pairing data retrieved from Redis
        """
        self.cache.set_with_expiration(
            key=DEVICE_PAIRING_TOKEN_KEY.format(pairing_token=pairing_data["token"]),
            value=json.dumps(pairing_data),
            expiration=ONE_DAY,
        )

    def _add_pantacor_config(self, device_id: str, pairing_data: dict):
        """The software updates are managed by Pantacor, get their ID and add to DB

        :param device_id: internal identifier of the device
        :param pairing_data: data retrieved from the Redis cache for pairing
        """
        core_packaging = pairing_data.get("packaging_type")
        pairing_code = pairing_data["code"]
        if core_packaging is not None and core_packaging == "pantacor":
            pantacor_config = get_pantacor_device(pairing_code)
            self.device_repository.add_pantacor_config(device_id, pantacor_config)

    def delete(self, device_id: str):
        """Handle an HTTP DELETE request.

        :param device_id: database identifier of a device
        """
        self._authenticate()
        self._delete_device(device_id)

        return "", HTTPStatus.NO_CONTENT

    def _delete_device(self, device_id: str):
        """Delete the specified device from the database.

        There are other tables related to the device table in the database.  This
        method assumes that the child tables contain "delete cascade" clauses.

        :param device_id: database identifier of a device
        """
        self.device_repository.remove(device_id)
        delete_device_login(device_id, self.cache)

    def patch(self, device_id: str):
        """Handle a HTTP PATCH request.

        :param device_id: database identifier of a device
        """
        self._authenticate()
        updates = self._validate_request()
        self._update_device(device_id, updates)
        self.etag_manager.expire_device_etag_by_device_id(device_id)
        self.etag_manager.expire_device_location_etag_by_device_id(device_id)
        self.etag_manager.expire_device_setting_etag_by_device_id(device_id)

        return "", HTTPStatus.NO_CONTENT

    def _update_device(self, device_id: str, updates: dict):
        """Update the device attributes on the database based on the request.

        :param device_id: database identifier of a device
        :param updates: The new values of the device attributes
        """
        geography_id = self._ensure_geography_exists(updates)
        updates.update(geography_id=geography_id)
        pantacor_updates = dict(
            auto_update=updates.pop("auto_update"),
            release_channel=updates.pop("release_channel").lower(),
            ssh_public_key=updates.pop("ssh_public_key"),
        )
        self.device_repository.update_device_from_account(
            self.account.id, device_id, updates
        )
        self._update_pantacor_config(device_id, pantacor_updates)

    def _update_pantacor_config(self, device_id: str, updates: dict):
        """Update the Pantacor configuration on the database based on the request.

        :param device_id: database identifier of a device
        :param updates: The new values of the pantacor configuration attributes
        """
        device = self.device_repository.get_device_by_id(device_id)
        if device.pantacor_config.pantacor_id is not None:
            pantacor_update_functions = dict(
                auto_update=change_pantacor_update_policy,
                release_channel=change_pantacor_release_channel,
                ssh_public_key=change_pantacor_ssh_key,
            )
            current_config = asdict(device.pantacor_config)
            for config_name in ("auto_update", "release_channel", "ssh_public_key"):
                if current_config[config_name] != updates[config_name]:
                    update_function = pantacor_update_functions[config_name]
                    update_function(current_config["pantacor_id"], updates[config_name])
            self.device_repository.update_pantacor_config(device_id, updates)
