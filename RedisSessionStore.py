



class SessionStore:
    """Store session data in Redis."""

    def __init__(self, token, url='redis://localhost:6379', ttl=10):
        self.token = token
        self.redis = redis.Redis.from_url(url)
        self.ttl = ttl

    def set(self, key, value):
        self.refresh()
        return self.redis.hset(self.token, key, value)

    def get(self, key, value):
        self.refresh()
        return self.redis.hget(self.token, key)

    def incr(self, key):
        self.refresh()
        return self.redis.hincrby(self.token, key, 1)

    def refresh(self):
        self.redis.expire(self.token, self.ttl)