from __future__ import annotations

import time
from threading import RLock


class TTLCache:
    def __init__(self):
        self._data = {}
        self._lock = RLock()

    def get(self, key):
        now = time.time()
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None, False
            expires_at, value = item
            if expires_at <= now:
                self._data.pop(key, None)
                return None, False
            return value, True

    def set(self, key, value, ttl: int):
        if ttl <= 0:
            return
        with self._lock:
            self._data[key] = (time.time() + ttl, value)

    def clear(self):
        with self._lock:
            self._data.clear()


cache = TTLCache()
