import time

from django.core.cache import cache


class Cache(object):

    def get(self, key, default=None):
        if default is None:
            default = {}

        if self._has_expired(key):
            cache.delete(key)

        return cache.get(key, default).get('value')

    def set(self, key, value, timeout=None):
        now = time.time()
        cache.set(key, dict(value=value, start=now, timeout=timeout))

    def time_remaining(self, key):
        item = cache.get(key)
        if item is None or item['timeout'] is None:
            return
        elapsed = time.time() - item['start']
        time_remaining = item['timeout'] - elapsed
        if time_remaining < 0:
            cache.delete(key)
            return
        return time_remaining

    def _has_expired(self, key):
        return self.time_remaining(key) == 0
