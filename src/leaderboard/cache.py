import time

from django.core.cache import cache


PLAYERS_CACHE_TIMEOUT = 30


class LeaderboardCache(object):
    """
    Helper class to increase latency and reduce resource use when polling the
    leaderboard API.
    """

    DEFAULT_CACHE_TIMEOUT = PLAYERS_CACHE_TIMEOUT # seconds

    def get(self, key, default=None):
        if default is None:
            default = {}

        if self._has_expired(key):
            cache.delete(key)

        return cache.get(key, default).get('value')

    def set(self, key, value, timeout=None):
        now = time.time()
        timeout = (
            self.DEFAULT_CACHE_TIMEOUT if timeout is None else timeout
        )
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
