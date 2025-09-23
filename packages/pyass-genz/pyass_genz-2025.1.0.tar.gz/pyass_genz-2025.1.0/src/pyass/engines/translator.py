# pyass🍑/src/pyass/engines/translator.py

import random
import re
from typing import Optional, Dict, List, Any
from ..core.models import SlangFilter
from ..core.slangdb import get_slang_db
from ..core.config import PyAssConfig

class Translator:
    """
    Translate boring English into ✨vibe✨ language.
    Configurable by tone, intensity, platform.
    """

    def __init__(self):
        self.db = get_slang_db()
        self.config = PyAssConfig.get()

        # Base word → slang mappings (expandable)
        self.base_replacements = {
            "good": ["bussin", "slay", "ate", "goated"],
            "bad": ["ick", "mid", "cheugy", "beige flag"],
            "cool": ["slay", "based", "sigma", "iconic"],
            "crazy": ["skibidi", "unhinged", "feral", "chaos mode"],
            "beautiful": ["gyatt", "snatched", "serving face", "looksmaxxed"],
            "tired": ["unalived", "not alive", "in shambles", "bed rotting"],
            "funny": ["I'm deceased", "send help", "this is violence", "gagging"],
            "yes": ["bet", "fr", "yas", "periodt"],
            "no": ["nah", "cap", "big yikes", "touch grass"],
            "hello": ["it's giving... entrance", "sheesh", "what it do"],
            "bye": ["glazing u fr", "touch grass 👋", "I'm out"],
            "please": ["gyatt please", "mood", "vibe check?"],
            "thank you": ["glazing u fr", "you're a whole snack", "mother"],
            "sorry": ["my bad", "I'm in my flop era", "send help"],
            "love": ["stan", "attached", "rent free in my head"],
            "hate": ["ick", "NPC behavior", "unalive this"],
            "talk": ["yap", "spill the tea", "read me"],
            "eat": ["bussin", "girl dinner", "fit check"],
            "work": ["werk", "hustle", "lazy girl job", "soft life"],
        }

    def translate(
        self,
        text: str,
        tone: str = "casual",
        intensity: float = 0.7,
        platform: Optional[str] = None,
        persona: Optional[str] = None
    ) -> str:
        """
        Translate text into Gen-Z slang.

        Args:
            text: Input text
            tone: "casual", "dramatic", "meme", "corporate_genz"
            intensity: 0.0 (minimal slang) to 1.0 (maximum chaos)
            platform: Override config platform (e.g., "TikTok", "Twitter")
            persona: "sigma", "main_character", "npc", etc. — overrides vibe

        Returns:
            Translated text with ✨vibes✨
        """
        if not text.strip():
            return text

        platform = platform or self.config.default_platform
        words = re.split(r'(\W+)', text)  # Keep punctuation

        result = []
        for word in words:
            if not word.isalpha():
                result.append(word)
                continue

            # Skip if random says no (based on intensity)
            if random.random() > intensity:
                result.append(word)
                continue

            # Get replacements
            replacements = self._get_replacements(word.lower(), platform, persona, tone)

            if replacements:
                chosen = random.choice(replacements)
                # Preserve case
                if word.isupper():
                    chosen = chosen.upper()
                elif word[0].isupper():
                    chosen = chosen.capitalize()
                result.append(chosen)
            else:
                result.append(word)

        return "".join(result)

    def _get_replacements(self, word: str, platform: str, persona: Optional[str], tone: str) -> List[str]:
        """Get slang replacements for a word based on context"""
        replacements = []

        # Base dictionary
        if word in self.base_replacements:
            replacements.extend(self.base_replacements[word])

        # Search DB for related terms
        filter_tags = []
        if persona:
            filter_tags.append(persona)
        if tone == "dramatic":
            filter_tags.extend(["villain_era", "main_character", "chaos"])
        elif tone == "meme":
            filter_tags.extend(["skibidi", "delulu", "gremlin"])

        if filter_tags:
            slang_entries = self.db.search(
                SlangFilter(
                    term_contains=word,
                    platforms=[platform] if platform else None,
                    vibe_tags=filter_tags,
                    min_popularity=50
                )
            )
            replacements.extend([e.term for e in slang_entries])

        # Remove duplicates
        return list(dict.fromkeys(replacements))

    def batch_translate(self, texts: List[str], **kwargs) -> List[str]:
        """Translate multiple texts"""
        return [self.translate(text, **kwargs) for text in texts]

    def explain_translation(self, text: str, **kwargs) -> Dict[str, Any]:
        """Returns translation + metadata for debugging/learning"""
        translated = self.translate(text, **kwargs)
        return {
            "original": text,
            "translated": translated,
            "intensity": kwargs.get("intensity", 0.7),
            "platform": kwargs.get("platform", self.config.default_platform),
            "persona": kwargs.get("persona"),
            "tone": kwargs.get("tone", "casual"),
        }
