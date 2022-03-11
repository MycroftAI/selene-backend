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

import random
import string

from selene.data.device import DeviceRepository
from selene.util.cache import SeleneCache, DEVICE_SKILL_ETAG_KEY
from selene.util.db import connect_to_db

ETAG_REQUEST_HEADER_KEY = "If-None-Match"


def device_etag_key(device_id: str):
    return "device.etag:{uuid}".format(uuid=device_id)


def device_setting_etag_key(device_id: str):
    return "device.setting.etag:{uuid}".format(uuid=device_id)


def device_location_etag_key(device_id: str):
    return "device.location.etag:{uuid}".format(uuid=device_id)


class ETagManager(object):
    """Class responsible for generate and expire etags"""

    etag_chars = string.ascii_letters + string.digits

    def __init__(self, cache: SeleneCache, config: dict):
        self.cache: SeleneCache = cache
        self.db_connection_config = config["DB_CONNECTION_CONFIG"]

    def get(self, key: str) -> str:
        """Generate a etag with 32 random chars and store it into a given key
        :param key: key where the etag will be stored
        :return etag"""
        etag = self.cache.get(key)
        if etag is None:
            etag = "".join(random.choice(self.etag_chars) for _ in range(32))
            self.cache.set(key, etag)
        return etag

    def expire(self, key):
        """Expires an existent etag
        :param key: key where the etag is stored"""
        etag = "".join(random.choice(self.etag_chars) for _ in range(32))
        self.cache.set(key, etag)

    def expire_device_etag_by_device_id(self, device_id: str):
        """Expire the etag associated with a device entity
        :param device_id: device uuid"""
        self.expire(device_etag_key(device_id))

    def expire_device_setting_etag_by_device_id(self, device_id: str):
        """Expire the etag associated with a device's settings entity
        :param device_id: device uuid"""
        self.expire(device_setting_etag_key(device_id))

    def expire_device_setting_etag_by_account_id(self, account_id: str):
        """Expire the settings' etags for all devices from a given account. Used when the settings are updated
        at account level"""
        db = connect_to_db(self.db_connection_config)
        devices = DeviceRepository(db).get_devices_by_account_id(account_id)
        for device in devices:
            self.expire_device_setting_etag_by_device_id(device.id)

    def expire_device_location_etag_by_device_id(self, device_id: str):
        """Expire the etag associate with the device's location entity
        :param device_id: device uuid"""
        self.expire(device_location_etag_key(device_id))

    def expire_device_location_etag_by_account_id(self, account_id: str):
        """Expire the locations' etag fpr açç device for a given acccount
        :param account_id: account uuid"""
        db = connect_to_db(self.db_connection_config)
        devices = DeviceRepository(db).get_devices_by_account_id(account_id)
        for device in devices:
            self.expire_device_location_etag_by_device_id(device.id)

    def expire_skill_etag_by_device_id(self, device_id):
        """Expire the locations' etag for a given device

        :param device_id: device uuid
        """
        self.expire(DEVICE_SKILL_ETAG_KEY.format(device_id=device_id))

    def expire_skill_etag_by_account_id(self, account_id):
        db = connect_to_db(self.db_connection_config)
        devices = DeviceRepository(db).get_devices_by_account_id(account_id)
        for device in devices:
            self.expire_skill_etag_by_device_id(device.id)
