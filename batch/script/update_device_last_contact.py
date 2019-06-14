from datetime import datetime

from selene.batch import SeleneScript
from selene.data.device import DeviceRepository
from selene.util.cache import SeleneCache, DEVICE_LAST_CONTACT_KEY


class UpdateDeviceLastContact(SeleneScript):
    def __init__(self):
        super(UpdateDeviceLastContact, self).__init__(__file__)
        self.cache = SeleneCache()

    def _run(self):
        device_repo = DeviceRepository(self.db)
        devices_updated = 0
        for device in device_repo.get_all_device_ids():
            last_contact_ts = self._get_ts_from_cache(device.id)
            if last_contact_ts is not None:
                devices_updated += 1
                device_repo.update_last_contact_ts(device.id, last_contact_ts)

        self.log.info(str(devices_updated) + ' devices were active today')

    def _get_ts_from_cache(self, device_id):
        last_contact_ts = None
        cache_key = DEVICE_LAST_CONTACT_KEY.format(device_id)
        value = self.cache.get(cache_key)
        if value is not None:
            last_contact_ts = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')

        return last_contact_ts


UpdateDeviceLastContact().run()
