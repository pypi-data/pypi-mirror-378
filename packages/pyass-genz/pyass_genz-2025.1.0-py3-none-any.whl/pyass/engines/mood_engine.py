# pyass🍑/src/pyass/engines/mood_engine.py

import random
from typing import List, Optional
from ..core.models import SlangEntry, SlangFilter
from ..core.slangdb import get_slang_db

class MoodEngine:
    """
    Generate slang based on persona, mood, or vibe.
    """

    PERSONA_PRESETS = {
        "main_character": {
            "vibe_tags": ["main_character", "slay", "iconic", "villain_era"],
            "min_popularity": 70,
            "description": "You’re the star. Everything is a scene."
        },
        "sigma": {
            "vibe_tags": ["sigma", "based", "lone_wolf", "no_talk"],
            "min_popularity": 50,
            "description": "Silent. Mysterious. Always winning."
        },
        "npc": {
            "vibe_tags": ["npc", "mid", "basic", "beige_flag"],
            "max_popularity": 60,
            "description": "Just here. No thoughts. Repeat trends."
        },
        "chaos_goblin": {
            "vibe_tags": ["chaos", "skibidi", "gremlin", "unhinged"],
            "min_popularity": 40,
            "description": "Breaks norms. Loves mess. Sends it."
        },
        "pick_me": {
            "vibe_tags": ["pick_me", "simp", "trauma_dump", "yapping"],
            "description": "Seeks validation. Puts others down."
        },
        "glow_up_queen": {
            "vibe_tags": ["glow_up", "soft_era", "clean_girl", "that_girl"],
            "min_popularity": 60,
            "description": "Self-care. Aesthetic. Evolving."
        },
        "delulu": {
            "vibe_tags": ["delulu", "romantasy", "attached", "I_can't"],
            "description": "Delusionally optimistic. It’s a lifestyle."
        },
        "touch_grass": {
            "vibe_tags": ["touch_grass", "unalived", "bed_rotting", "soft_life"],
            "description": "Offline. Resting. Rejecting hustle."
        }
    }

    def __init__(self):
        self.db = get_slang_db()

    def get_by_persona(self, persona: str, count: int = 5) -> List[SlangEntry]:
        """Get slang matching a persona preset"""
        if persona not in self.PERSONA_PRESETS:
            raise ValueError(f"Unknown persona '{persona}'. Try: {list(self.PERSONA_PRESETS.keys())}")

        preset = self.PERSONA_PRESETS[persona]
        filter_config = SlangFilter(
            vibe_tags=preset.get("vibe_tags"),
            min_popularity=preset.get("min_popularity", 0),
            max_popularity=preset.get("max_popularity", 100),
            exclude_offensive=False  # Personas might want offensive terms
        )

        results = self.db.search(filter_config)
        if not results:
            # Fallback: any slang with persona in vibe_tags
            results = self.db.search(SlangFilter(vibe_tags=[persona]))

        return random.sample(results, min(count, len(results))) if results else []

    def get_by_vibe(self, vibe_tags: List[str], count: int = 5, era: Optional[str] = None) -> List[SlangEntry]:
        """Get slang by custom vibe tags"""
        filter_config = SlangFilter(
            vibe_tags=vibe_tags,
            era_start=era,
            era_end=era if era else None
        )
        results = self.db.search(filter_config)
        return random.sample(results, min(count, len(results))) if results else []

    def get_trending(self, region: Optional[str] = None, platform: Optional[str] = None, count: int = 10) -> List[SlangEntry]:
        """Get currently trending slang"""
        filter_config = SlangFilter(
            min_popularity=80,
            regions=[region] if region else None,
            platforms=[platform] if platform else None
        )
        results = self.db.search(filter_config)
        # Sort by popularity
        results.sort(key=lambda x: x.popularity_score, reverse=True)
        return results[:count]

    def get_vintage(self, count: int = 5) -> List[SlangEntry]:
        """Get 'vintage' slang (low popularity but high revival potential)"""
        # In our dataset, we don't have revival_potential yet — so we fake it
        # Vintage = low pop, not offensive, from 2020-2022
        filter_config = SlangFilter(
            min_popularity=20,
            max_popularity=50,
            exclude_offensive=True,
            era_start="2020Q1",
            era_end="2022Q4"
        )
        results = self.db.search(filter_config)
        return random.sample(results, min(count, len(results))) if results else []

    def get_random_vibe(self) -> str:
        """Get a random persona/vibe name"""
        return random.choice(list(self.PERSONA_PRESETS.keys()))

    def describe_persona(self, persona: str) -> Optional[str]:
        """Get description of a persona"""
        return self.PERSONA_PRESETS.get(persona, {}).get("description")
