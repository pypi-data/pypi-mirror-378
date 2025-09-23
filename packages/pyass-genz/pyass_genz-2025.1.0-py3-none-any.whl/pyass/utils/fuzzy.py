# pyass🍑/src/pyass/utils/fuzzy.py

import re
from typing import List, Tuple
import difflib

try:
    import Levenshtein
except ImportError:
    Levenshtein = None

class FuzzyMatcher:
    """
    Advanced fuzzy string matching for slang terms.
    Falls back gracefully if optional deps not installed.
    """

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if Levenshtein:
            return Levenshtein.distance(s1, s2)
        else:
            # Fallback to difflib
            return FuzzyMatcher._fallback_levenshtein(s1, s2)

    @staticmethod
    def _fallback_levenshtein(s1: str, s2: str) -> int:
        """Fallback Levenshtein using dynamic programming"""
        if len(s1) < len(s2):
            return FuzzyMatcher._fallback_levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def similarity_ratio(s1: str, s2: str) -> float:
        """Return similarity ratio 0.0 - 1.0"""
        if Levenshtein:
            return Levenshtein.ratio(s1, s2)
        else:
            return difflib.SequenceMatcher(None, s1, s2).ratio()

    @staticmethod
    def soundex(s: str) -> str:
        """
        Soundex phonetic algorithm — groups similar sounding words.
        Basic implementation.
        """
        if not s:
            return "0000"

        s = s.upper()
        soundex_code = s[0]
        consonant_codes = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6'
        }

        for char in s[1:]:
            code = consonant_codes.get(char, '')
            if code and (not soundex_code or code != soundex_code[-1]):
                soundex_code += code

        # Pad or truncate to 4 chars
        soundex_code = soundex_code[:4].ljust(4, '0')
        return soundex_code

    @staticmethod
    def match_with_soundex(target: str, candidates: List[str], threshold: float = 0.0) -> List[Tuple[str, float]]:
        """Match using soundex + similarity fallback"""
        target_soundex = FuzzyMatcher.soundex(target)
        results = []

        for candidate in candidates:
            cand_soundex = FuzzyMatcher.soundex(candidate)
            if cand_soundex == target_soundex:
                similarity = FuzzyMatcher.similarity_ratio(target, candidate)
                if similarity >= threshold:
                    results.append((candidate, similarity))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def find_best_match(query: str, candidates: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """Find top K best matches using similarity ratio"""
        scored = [(cand, FuzzyMatcher.similarity_ratio(query, cand)) for cand in candidates]
        scored = [item for item in scored if item[1] > 0.0]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for matching: lower, remove punctuation"""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return re.sub(r'\s+', ' ', text).strip()
