from http import HTTPStatus
from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


class DeviceCountEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        device_count = self._get_devices()

        return dict(deviceCount=device_count), HTTPStatus.OK

    def _get_devices(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device_repository = DeviceRepository(db)
            device_count = device_repository.get_account_device_count(
                self.account.id
            )

            return device_count
