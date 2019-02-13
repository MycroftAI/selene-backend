import os

from redis import Redis


class SeleneCache(object):

    def __init__(self):
        # should the variables host and port be in the config class?
        redis_host = os.environ['REDIS_HOST']
        redis_port = int(os.environ['REDIS_PORT'])
        self.redis = Redis(host=redis_host, port=redis_port)

    def set_if_not_exists_with_expiration(self, key, value, expiration):
        """Sets a key only if it doesn't exist and using a given expiration time"""
        return self.redis.set(name=key, value=value, ex=expiration, nx=True)
