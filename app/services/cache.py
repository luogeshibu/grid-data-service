from __future__ import annotations

import time
from typing import Any


class TTLCache:
    def __init__(self, max_entries: int = 10_000):
        self._items: dict[tuple, tuple[float, Any]] = {}
        self.max_entries = max_entries

    def get(self, key: tuple) -> tuple[Any, bool]:
        item = self._items.get(key)
        if item is None:
            return None, False

        expires_at, value = item
        if expires_at <= time.monotonic():
            self._items.pop(key, None)
            return None, False

        return value, True

    def set(self, key: tuple, value: Any, ttl_seconds: int) -> None:
        if ttl_seconds > 0:
            if len(self._items) >= self.max_entries and key not in self._items:
                oldest_key = min(self._items, key=lambda candidate: self._items[candidate][0])
                self._items.pop(oldest_key, None)
            self._items[key] = (time.monotonic() + ttl_seconds, value)

    def clear(self) -> None:
        self._items.clear()
