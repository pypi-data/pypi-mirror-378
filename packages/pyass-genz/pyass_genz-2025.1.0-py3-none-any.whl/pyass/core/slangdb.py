# pyass🍑/src/pyass/core/slangdb.py

import json
import random
from typing import List, Optional, Dict, Any, Iterator

from .models import SlangEntry, SlangFilter
from .config import PyAssConfig
from .cache import GLOBAL_CACHE

class SlangDB:
    """
    Main interface to access, search, and interact with the slang database.
    Singleton-like — load once, use everywhere.
    """

    def __init__(self):
        self.config = PyAssConfig.get()
        self.entries: List[SlangEntry] = []
        self.term_index: Dict[str, SlangEntry] = {}
        self._loaded = False

    def load(self, filepath: Optional[str] = None):
        """Load slang data from JSON file or package resource"""
        if self._loaded:
            return

        import importlib.resources as resources
        if filepath is None:
            # Try to load from package resource
            try:
                with resources.files("pyass.data").joinpath("base_slang.json").open("r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            except Exception as e:
                raise RuntimeError(f"Failed to load slang DB from package resource: {e}")
        else:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
            except Exception as e:
                raise RuntimeError(f"Failed to load slang DB from {filepath}: {e}")

        self.entries = [SlangEntry(**item) for item in raw_data]
        self.term_index = {entry.term.lower(): entry for entry in self.entries}
        self._loaded = True

    def get(self, term: str) -> Optional[SlangEntry]:
        """Get slang by exact term (case-insensitive) — uses cache"""
        term_lower = term.lower().strip()
        cached = GLOBAL_CACHE.get(term_lower)
        if cached:
            return SlangEntry(**cached)

        entry = self.term_index.get(term_lower)
        if entry:
            GLOBAL_CACHE.set(term_lower, entry.dict())
        return entry

    def search(self, filter: SlangFilter) -> List[SlangEntry]:
        """Advanced search with filters"""
        results = []

        for entry in self.entries:
            # Term contains
            if filter.term_contains and filter.term_contains.lower() not in entry.term.lower():
                continue

            # Popularity
            if not (filter.min_popularity <= entry.popularity_score <= filter.max_popularity):
                continue

            # Region
            if filter.regions and entry.region not in filter.regions:
                continue

            # Platform
            if filter.platforms and entry.platform not in filter.platforms:
                continue

            # Vibe tags (ANY match)
            if filter.vibe_tags and not any(tag in entry.vibe_tags for tag in filter.vibe_tags):
                continue

            # Era (simple string compare — assumes "YYYYQn" format)
            if filter.era_start:
                if entry.era < filter.era_start:
                    continue
            if filter.era_end:
                if entry.era > filter.era_end:
                    continue

            # Offensive filter
            if filter.exclude_offensive and entry.is_offensive:
                continue

            results.append(entry)

        return results

    def random(self, count: int = 1, filter: Optional[SlangFilter] = None) -> List[SlangEntry]:
        """Get random slang entries, optionally filtered"""
        pool = self.search(filter) if filter else self.entries
        if not pool:
            return []
        return random.sample(pool, min(count, len(pool)))

    def stats(self) -> Dict[str, Any]:
        """Return database statistics"""
        if not self._loaded:
            self.load()

        eras = [e.era for e in self.entries]
        regions = [e.region for e in self.entries]
        platforms = [e.platform for e in self.entries]
        vibes = [v for e in self.entries for v in e.vibe_tags]

        return {
            "total_entries": len(self.entries),
            "unique_terms": len(self.term_index),
            "eras": sorted(set(eras)),
            "regions": sorted(set(regions)),
            "platforms": sorted(set(platforms)),
            "top_vibes": sorted(set(vibes), key=vibes.count, reverse=True)[:10],
            "avg_popularity": sum(e.popularity_score for e in self.entries) / len(self.entries),
            "offensive_count": sum(1 for e in self.entries if e.is_offensive),
        }

    def __len__(self):
        return len(self.entries) if self._loaded else 0

    def __contains__(self, term: str):
        return term.lower().strip() in self.term_index

    def __iter__(self) -> "Iterator[SlangEntry]":
        return iter(self.entries)

# Global instance — use SlangDB.get_instance()
class _SlangDBSingleton:
    _instance: Optional[SlangDB] = None

    @classmethod
    def get_instance(cls) -> SlangDB:
        if cls._instance is None:
            cls._instance = SlangDB()
            cls._instance.load()
        return cls._instance

# Export this
get_slang_db = _SlangDBSingleton.get_instance
