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

import os

from redis import Redis

DEVICE_LAST_CONTACT_KEY = 'device:last_contact:{device_id}'
DEVICE_SKILL_ETAG_KEY = 'device.skill.etag:{device_id}'
DEVICE_PAIRING_CODE_KEY = 'pairing.code:{pairing_code}'
DEVICE_PAIRING_TOKEN_KEY = 'pairing.token:{pairing_token}'


class SeleneCache(object):

    def __init__(self):
        # should the variables host and port be in the config class?
        redis_host = os.environ['REDIS_HOST']
        redis_port = int(os.environ['REDIS_PORT'])
        self.redis = Redis(host=redis_host, port=redis_port)

    def set_if_not_exists_with_expiration(
            self, key: str, value: str, expiration: int
    ) -> bool:
        """Sets a key only if it doesn't exist and using a given expiration time

        :return True if the set operation is successful, False if not.  Will
            return False if the value already exists for this key
        """
        if expiration > 0:
            # Setting the "nx" argument to True will ensure the set will fail
            # if a value already exists for this key.
            return self.redis.set(name=key, value=value, ex=expiration, nx=True)

    def set_with_expiration(self, key, value, expiration: int):
        """Sets a key with a given expiration"""
        if expiration > 0:
            return self.redis.set(name=key, value=value, ex=expiration)

    def get(self, key):
        """Returns the value stored in a key"""
        return self.redis.get(name=key)

    def delete(self, key):
        """Deletes a key from the cache"""
        return self.redis.delete(key)

    def set(self, key, value):
        """Sets a key with a given value"""
        return self.redis.set(name=key, value=value)
