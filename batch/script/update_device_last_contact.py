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

"""Update last contact timestamp of devices that had activity

As devices make API calls throughout the day, they store a timestamp of the
API call in Redis.  This is done to take some load off of the Postgres database
throughout the day.

This script should run on a daily basis to update the Postgres database with
the values on the Redis database.
"""
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
        cache_key = DEVICE_LAST_CONTACT_KEY.format(device_id=device_id)
        value = self.cache.get(cache_key)
        if value is not None:
            last_contact_ts = datetime.strptime(
                value.decode(),
                '%Y-%m-%d %H:%M:%S.%f'
            )
            self.cache.delete(cache_key)

        return last_contact_ts


if __name__ == '__main__':
    UpdateDeviceLastContact().run()
