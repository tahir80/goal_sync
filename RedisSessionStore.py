import redis
from os import environ

class RedisDataStore:
    def __init__(self, host=environ.get('REDIS_HOST'), port=environ.get('REDIS_PORT'), db=0):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)

    def set_data(self, key, value, expiration=None):
        self.redis_client.set(key, value)
        if expiration is not None:
            self.redis_client.expire(key, expiration)

    def get_data(self, key):
        return self.redis_client.get(key)

    def delete_data(self, key):
        self.redis_client.delete(key)

    def get_all_keys(self):
        return self.redis_client.keys('*')
