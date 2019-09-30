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
from datetime import datetime, timedelta
from http import HTTPStatus
from logging import getLogger

from flask import json
from schematics import Model
from schematics.exceptions import ValidationError
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.api.etag import ETagManager
from selene.api.public_endpoint import delete_device_login
from selene.data.device import DeviceRepository, Geography, GeographyRepository
from selene.util.cache import DEVICE_LAST_CONTACT_KEY, SeleneCache

ONE_DAY = 86400
CONNECTED = 'Connected'
DISCONNECTED = 'Disconnected'
DORMANT = 'Dormant'

_log = getLogger()


def validate_pairing_code(pairing_code):
    cache_key = 'pairing.code:' + pairing_code
    cache = SeleneCache()
    pairing_cache = cache.get(cache_key)

    if pairing_cache is None:
        raise ValidationError('pairing code not found')


class UpdateDeviceRequest(Model):
    city = StringType(required=True)
    country = StringType(required=True)
    name = StringType(required=True)
    placement = StringType()
    region = StringType(required=True)
    timezone = StringType(required=True)
    wake_word = StringType(required=True)
    voice = StringType(required=True)


class NewDeviceRequest(UpdateDeviceRequest):
    pairing_code = StringType(required=True, validators=[validate_pairing_code])


class DeviceEndpoint(SeleneEndpoint):
    def __init__(self):
        super(DeviceEndpoint, self).__init__()
        self.devices = None
        self.cache = self.config['SELENE_CACHE']
        self.etag_manager: ETagManager = ETagManager(self.cache, self.config)

    def get(self, device_id):
        self._authenticate()
        if device_id is None:
            response_data = self._get_devices()
        else:
            response_data = self._get_device(device_id)

        return response_data, HTTPStatus.OK

    def _get_devices(self):
        device_repository = DeviceRepository(self.db)
        devices = device_repository.get_devices_by_account_id(
            self.account.id
        )
        response_data = []
        for device in devices:
            response_device = self._format_device_for_response(device)
            response_data.append(response_device)

        return response_data

    def _get_device(self, device_id):
        device_repository = DeviceRepository(self.db)
        device = device_repository.get_device_by_id(device_id)
        response_data = self._format_device_for_response(device)

        return response_data

    def _format_device_for_response(self, device):
        """Convert device object into a response object for this endpoint."""
        last_contact_age = self._get_device_last_contact(device)
        device_status = self._determine_device_status(last_contact_age)
        if device_status == DISCONNECTED:
            disconnect_duration = self._determine_disconnect_duration(
                last_contact_age
            )
        else:
            disconnect_duration = None
        device_dict = asdict(device)
        device_dict['status'] = device_status
        device_dict['disconnect_duration'] = disconnect_duration
        device_dict['voice'] = device_dict.pop('text_to_speech')

        return device_dict

    def _get_device_last_contact(self, device):
        """Get the last time the device contacted the backend.

        The timestamp returned by this method will be used to determine if a
        device is active or not.

        The device table has a last contacted column but it is only updated
        daily via batch script.  The real-time values are kept in Redis.
        If the Redis query returns nothing, the device hasn't contacted the
        backend yet.  This could be because it was just activated. Give the
        device a couple of minutes to make that first call to the backend.
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
            last_contact_ts = datetime.strptime(
                last_contact_ts,
                '%Y-%m-%d %H:%M:%S.%f'
            )
            last_contact_age = datetime.utcnow() - last_contact_ts

        return last_contact_age

    @staticmethod
    def _determine_device_status(last_contact_age):
        """Derive device status from the last time device contacted servers."""
        if last_contact_age <= timedelta(seconds=120):
            device_status = CONNECTED
        elif timedelta(seconds=120) < last_contact_age < timedelta(days=30):
            device_status = DISCONNECTED
        else:
            device_status = DORMANT

        return device_status

    @staticmethod
    def _determine_disconnect_duration(last_contact_age):
        """Derive device status from the last time device contacted servers."""
        disconnect_duration = 'unknown'
        days, _ = divmod(last_contact_age, timedelta(days=1))
        if days:
            disconnect_duration = str(days) + ' days'
        else:
            hours, remaining = divmod(last_contact_age, timedelta(hours=1))
            if hours:
                disconnect_duration = str(hours) + ' hours'
            else:
                minutes, _ = divmod(remaining, timedelta(minutes=1))
                if minutes:
                    disconnect_duration = str(minutes) + ' minutes'

        return disconnect_duration

    def post(self):
        self._authenticate()
        device = self._validate_request()
        device_id = self._pair_device(device)

        return device_id, HTTPStatus.OK

    def _validate_request(self):
        request_data = json.loads(self.request.data)
        if self.request.method == 'POST':
            device = NewDeviceRequest()
            device.pairing_code = request_data['pairingCode']
        else:
            device = UpdateDeviceRequest()
        device.city = request_data['city']
        device.country = request_data['country']
        device.name = request_data['name']
        device.placement = request_data['placement']
        device.region = request_data['region']
        device.timezone = request_data['timezone']
        device.wake_word = request_data['wakeWord']
        device.voice = request_data['voice']
        device.validate()

        return device

    def _pair_device(self, device):
        self.db.autocommit = False
        try:
            pairing_data = self._get_pairing_data(device.pairing_code)
            device_id = self._add_device(device)
            pairing_data['uuid'] = device_id
            self.cache.delete('pairing.code:{}'.format(device.pairing_code))
            self._build_pairing_token(pairing_data)
        except Exception:
            self.db.rollback()
            raise
        else:
            self.db.commit()

        return device_id

    def _get_pairing_data(self, pairing_code: str) -> dict:
        """Checking if there's one pairing session for the pairing code."""
        cache_key = 'pairing.code:' + pairing_code
        pairing_cache = self.cache.get(cache_key)
        pairing_data = json.loads(pairing_cache)

        return pairing_data

    def _add_device(self, device: NewDeviceRequest):
        """Creates a device and associate it to a pairing session"""
        device_dict = device.to_native()
        geography_id = self._ensure_geography_exists(self.db, device_dict)
        device_dict.update(geography_id=geography_id)
        device_repository = DeviceRepository(self.db)
        device_id = device_repository.add(self.account.id, device_dict)

        return device_id

    def _ensure_geography_exists(self, db, device: dict):
        geography = Geography(
            city=device['city'],
            country=device['country'],
            region=device['region'],
            time_zone=device['timezone']
        )
        geography_repository = GeographyRepository(db, self.account.id)
        geography_id = geography_repository.get_geography_id(geography)
        if geography_id is None:
            geography_id = geography_repository.add(geography)

        return geography_id

    def _build_pairing_token(self, pairing_data):
        self.cache.set_with_expiration(
            key='pairing.token:' + pairing_data['token'],
            value=json.dumps(pairing_data),
            expiration=ONE_DAY
        )

    def delete(self, device_id):
        self._authenticate()
        self._delete_device(device_id)
        return '', HTTPStatus.NO_CONTENT

    def _delete_device(self, device_id):
        device_repository = DeviceRepository(self.db)
        device_repository.remove(device_id)
        delete_device_login(device_id, self.cache)

    def patch(self, device_id):
        self._authenticate()
        updates = self._validate_request()
        self._update_device(device_id, updates)
        self.etag_manager.expire_device_etag_by_device_id(device_id)
        self.etag_manager.expire_device_location_etag_by_device_id(device_id)
        self.etag_manager.expire_device_setting_etag_by_device_id(device_id)

        return '', HTTPStatus.NO_CONTENT

    def _update_device(self, device_id, updates):
        device_updates = updates.to_native()
        geography_id = self._ensure_geography_exists(self.db, device_updates)
        device_updates.update(geography_id=geography_id)
        device_repository = DeviceRepository(self.db)
        device_repository.update_device_from_account(
            self.account.id,
            device_id,
            device_updates
        )
