# pyass🍑/src/pyass/core/cache.py

from typing import Optional, Any
from functools import lru_cache
import json
import os
import hashlib

class HybridCache:
    """
    Hybrid LRU + Disk Cache for slang entries.
    - LRU for hot terms
    - Disk for persistence across sessions
    """

    def __init__(self, maxsize: int = 1000, disk_cache_dir: str = ".pyass_cache"):
        self.maxsize = maxsize
        self.disk_cache_dir = disk_cache_dir
        os.makedirs(disk_cache_dir, exist_ok=True)
        self._lru_cache = lru_cache(maxsize=maxsize)(self._fetch_from_disk_or_none)

    def _make_key(self, term: str) -> str:
        return hashlib.md5(term.lower().strip().encode()).hexdigest()

    def _disk_path(self, term: str) -> str:
        key = self._make_key(term)
        return os.path.join(self.disk_cache_dir, f"{key}.json")

    def _fetch_from_disk_or_none(self, term: str) -> Optional[Any]:
        path = self._disk_path(term)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def get(self, term: str) -> Optional[Any]:
        return self._lru_cache(term)

    def set(self, term: str, value: Any):
        # Set in LRU
        self._lru_cache.cache_clear()  # reset to force reload next time (simpler than fancy invalidation)
        # Save to disk
        path = self._disk_path(term)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(value, f)
        except Exception:
            pass  # Fail silently — cache is optional

    def clear(self):
        """Clear both LRU and disk cache"""
        self._lru_cache.cache_clear()
        for file in os.listdir(self.disk_cache_dir):
            if file.endswith(".json"):
                os.remove(os.path.join(self.disk_cache_dir, file))

    def __len__(self):
        return len(self._lru_cache.cache_info())  # Approximate

# Global cache instance
GLOBAL_CACHE = HybridCache(maxsize=1000)
