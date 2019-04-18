from dataclasses import asdict
from http import HTTPStatus
from logging import getLogger

from flask import json
from schematics import Model
from schematics.exceptions import ValidationError
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.api.etag import ETagManager
from selene.data.device import DeviceRepository, Geography, GeographyRepository
from selene.util.cache import SeleneCache
from selene.util.db import get_db_connection

ONE_DAY = 86400

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
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device_repository = DeviceRepository(db)
            devices = device_repository.get_devices_by_account_id(
                self.account.id
            )
        response_data = []
        for device in devices:
            device_dict = asdict(device)
            device_dict['voice'] = device_dict.pop('text_to_speech')
            response_data.append(device_dict)

        return response_data

    def _get_device(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device_repository = DeviceRepository(db)
            device = device_repository.get_device_by_id(
                device_id
            )
        response_data = asdict(device)
        response_data['voice'] = response_data.pop('text_to_speech')

        return response_data

    def post(self):
        # TODO: Look into ways to improve this by passing IDs instead of names
        # This code was written to deal with it's author's ignorance with
        # angular forms (I can say that because I am the idiot).  If the
        # frontend can pass the IDs instead of the names, the queries run here
        # would be more efficient.
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
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            db.autocommit = False
            try:
                pairing_data = self._get_pairing_data(device.pairing_code)
                device_id = self._add_device(device)
                pairing_data['uuid'] = device_id
                self.cache.delete('pairing.code:{}'.format(device.pairing_code))
                self._build_pairing_token(pairing_data)
            except Exception:
                db.rollback()
                raise
            else:
                db.commit()

        return device_id

    def _get_pairing_data(self, pairing_code: str) -> dict:
        """Checking if there's one pairing session for the pairing code."""
        cache_key = 'pairing.code:' + pairing_code
        pairing_cache = self.cache.get(cache_key)
        pairing_data = json.loads(pairing_cache)

        return pairing_data

    def _add_device(self, device: NewDeviceRequest):
        """Creates a device and associate it to a pairing session"""
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device_dict = device.to_native()
            geography_id = self._ensure_geography_exists(db, device_dict)
            device_dict.update(geography_id=geography_id)
            device_repository = DeviceRepository(db)
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
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device_repository = DeviceRepository(db)
            device_repository.remove(device_id)

    def patch(self, device_id):
        self._authenticate()
        updates = self._validate_request()
        self._update_device(device_id, updates)
        self.etag_manager.expire_device_etag_by_device_id(device_id)
        self.etag_manager.expire_device_location_etag_by_device_id(device_id)

        return '', HTTPStatus.NO_CONTENT

    def _update_device(self, device_id, updates):
        device_updates = updates.to_native()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            geography_id = self._ensure_geography_exists(db, device_updates)
            device_updates.update(geography_id=geography_id)
            device_repository = DeviceRepository(db)
            device_repository.update_device_from_account(
                self.account.id,
                device_id,
                device_updates
            )
