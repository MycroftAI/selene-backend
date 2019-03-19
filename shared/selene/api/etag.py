import random
import string

from selene.data.device import DeviceRepository
from selene.util.cache import SeleneCache
from selene.util.db import get_db_connection


def device_etag_key(device_id: str):
    return 'device.etag:{uuid}'.format(uuid=device_id)


def device_setting_etag_key(device_id: str):
    return 'device.setting.etag:{uuid}'.format(uuid=device_id)


class ETagManager(object):
    """Class responsible for generate and expire etags"""

    etag_chars = string.ascii_letters + string.digits

    def __init__(self, cache: SeleneCache, config: dict):
        self.cache: SeleneCache = cache
        self.db_connection_pool = config['DB_CONNECTION_POOL']

    def get(self, key: str) -> str:
        """Generate a etag with 32 random chars and store it into a given key
        :param key: key where the etag will be stored
        :return etag"""
        etag = self.cache.get(key)
        if etag is None:
            etag = ''.join(random.choice(self.etag_chars) for _ in range(32))
            self.cache.set(key, etag)
        return etag

    def _expire(self, key):
        """Expires an existent etag
        :param key: key where the etag is stored"""
        etag = ''.join(random.choice(self.etag_chars) for _ in range(32))
        self.cache.set(key, etag)

    def expire_device_etag_by_device_id(self, device_id: str):
        """Expire the etag associated with a device entity
        :param device_id: device uuid"""
        self._expire(device_etag_key(device_id))

    def expire_device_setting_etag_by_device_id(self, device_id: str):
        """Expire the etag associated with a device's settings entity
        :param device_id: device uuid"""
        self._expire(device_setting_etag_key(device_id))

    def expire_device_setting_etag_by_account_id(self, account_id):
        """Expire the settings' etags for all devices from a given account. Used when the settings are updated
        at account level"""
        with get_db_connection(self.db_connection_pool) as db:
            devices = DeviceRepository(db).get_devices_by_account_id(account_id)
            for device in devices:
                self.expire_device_setting_etag_by_device_id(device.id)
