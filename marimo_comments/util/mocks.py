""" mock cache object """

class MockCache(object):
    cache = {}
    def set(self, key, value, expiration=None):
        self.cache[key] = value
    def get(self, key, default=None):
        return self.cache.get(key)
    def delete(self, key):
        del self.cache[key]
    def delete_many(self, keys):
        for key in keys:
            self.delete(key)
