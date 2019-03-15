from dataclasses import asdict
from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


class DeviceEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device_repository = DeviceRepository(db)
            devices = device_repository.get_devices_by_account_id(
                self.account.id
            )

        response_data = []
        for device in devices:
            wake_word = dict(
                id=device.wake_word.id,
                name=device.wake_word.wake_word
            )
            voice = dict(
                id=device.text_to_speech.id,
                name=device.text_to_speech.display_name
            )
            geography = dict(
                id=device.geography.id,
                country=device.geography.country,
                region=device.geography.state,
                city=device.geography.city,
                timezone=device.geography.time_zone,
                latitude=device.geography.latitude,
                longitude=device.geography.longitude
            )
            placement = dict(
                id=None,
                name=device.placement
            )
            response_data.append(
                dict(
                    core_version=device.core_version,
                    enclosure_version=device.enclosure_version,
                    id=device.id,
                    geography=geography,
                    name=device.name,
                    placement=placement,
                    platform=device.platform,
                    voice=voice,
                    wake_word=wake_word,
                )
            )

        return response_data, HTTPStatus.OK
