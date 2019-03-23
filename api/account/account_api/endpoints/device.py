from http import HTTPStatus
from logging import getLogger

from flask import json
from schematics import Model
from schematics.types import StringType
from schematics.exceptions import ValidationError

from selene.api import SeleneEndpoint
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


class NewDeviceRequest(Model):
    city = StringType(required=True)
    country = StringType(required=True)
    name = StringType(required=True)
    pairing_code = StringType(required=True, validators=[validate_pairing_code])
    placement = StringType()
    region = StringType(required=True)
    timezone = StringType(required=True)
    wake_word = StringType(required=True)
    voice = StringType(required=True)


class DeviceEndpoint(SeleneEndpoint):
    def __init__(self):
        super(DeviceEndpoint, self).__init__()
        self.devices = None
        self.cache = SeleneCache()

    def get(self):
        self._authenticate()
        self._get_devices()
        response_data = self._build_response()

        return response_data, HTTPStatus.OK

    def _get_devices(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device_repository = DeviceRepository(db)
            self.devices = device_repository.get_devices_by_account_id(
                self.account.id
            )

    def _build_response(self):
        response_data = []
        for device in self.devices:
            wake_word = dict(
                id=device.wake_word.id,
                name=device.wake_word.display_name
            )
            voice = dict(
                id=device.text_to_speech.id,
                name=device.text_to_speech.display_name
            )
            geography = dict(
                id=device.geography.id,
                country=device.geography.country,
                region=device.geography.region,
                city=device.geography.city,
                timezone=device.geography.time_zone,
                latitude=device.geography.latitude,
                longitude=device.geography.longitude
            )
            response_data.append(
                dict(
                    core_version=device.core_version,
                    enclosure_version=device.enclosure_version,
                    id=device.id,
                    geography=geography,
                    name=device.name,
                    placement=device.placement,
                    platform=device.platform,
                    voice=voice,
                    wake_word=wake_word,
                )
            )

        return response_data

    def post(self):
        self._authenticate()
        device = self._validate_request()
        device_id = self._pair_device(device)

        return device_id, HTTPStatus.OK

    def _validate_request(self) -> NewDeviceRequest:
        request_data = json.loads(self.request.data)
        device = NewDeviceRequest()
        device.city = request_data['city']
        device.country = request_data['country']
        device.name = request_data['name']
        device.pairing_code = request_data['pairingCode']
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
            self._ensure_geography_exists(db, device.to_native())
            device_repository = DeviceRepository(db)
            device_id = device_repository.add_device(
                self.account.id,
                device.to_native()
            )

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
            geography_repository.add(geography)

    def _build_pairing_token(self, pairing_data):
        self.cache.set_with_expiration(
            key='pairing.token:' + pairing_data['token'],
            value=json.dumps(pairing_data),
            expiration=ONE_DAY
        )
