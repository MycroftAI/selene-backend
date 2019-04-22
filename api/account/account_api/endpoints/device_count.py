from http import HTTPStatus
from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository


class DeviceCountEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        device_count = self._get_devices()

        return dict(deviceCount=device_count), HTTPStatus.OK

    def _get_devices(self):
        device_repository = DeviceRepository(self.db)
        device_count = device_repository.get_account_device_count(
            self.account.id
        )

        return device_count
