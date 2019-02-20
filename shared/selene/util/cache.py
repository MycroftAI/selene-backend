import os

from redis import Redis


class SeleneCache(object):

    def __init__(self):
        # should the variables host and port be in the config class?
        redis_host = os.environ['REDIS_HOST']
        redis_port = int(os.environ['REDIS_PORT'])
        self.redis = Redis(host=redis_host, port=redis_port)

    def set_if_not_exists_with_expiration(self, key, value, expiration: int):
        """Sets a key only if it doesn't exist and using a given expiration time"""
        if expiration > 0:
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
