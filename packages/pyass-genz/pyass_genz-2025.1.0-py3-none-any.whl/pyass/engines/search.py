# pyass🍑/src/pyass/engines/search.py

import re
from typing import List, Tuple
from difflib import SequenceMatcher
from ..core.models import SlangEntry, SlangFilter
from ..core.slangdb import get_slang_db

class SlangSearchEngine:
    """
    Advanced search with fuzzy matching.
    Future-ready for vector/semantic search.
    """

    def __init__(self):
        self.db = get_slang_db()

    def fuzzy_search(self, query: str, threshold: float = 0.6, limit: int = 10) -> List[Tuple[SlangEntry, float]]:
        """
        Fuzzy search by term similarity.

        Returns list of (entry, similarity_score) sorted by score desc.
        Similarity: 0.0 - 1.0 (1.0 = exact match)
        """
        if not query.strip():
            return []

        query_lower = query.lower().strip()
        scored_results = []

        for entry in self.db.entries:
            similarity = self._calculate_similarity(query_lower, entry.term.lower())
            if similarity >= threshold:
                scored_results.append((entry, similarity))

        # Sort by similarity desc
        scored_results.sort(key=lambda x: x[1], reverse=True)

        return scored_results[:limit]

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity using SequenceMatcher"""
        return SequenceMatcher(None, s1, s2).ratio()

    def keyword_search(self, keywords: List[str], operator: str = "AND") -> List[SlangEntry]:
        """
        Search by multiple keywords in definition or term.
        operator: "AND" (all keywords) or "OR" (any keyword)
        """
        results = []
        keywords_lower = [k.lower() for k in keywords]

        for entry in self.db.entries:
            term_match = any(k in entry.term.lower() for k in keywords_lower)
            def_match = any(k in entry.definition.lower() for k in keywords_lower)

            if operator == "AND":
                if term_match and def_match:
                    results.append(entry)
            else:  # OR
                if term_match or def_match:
                    results.append(entry)

        return results

    def regex_search(self, pattern: str) -> List[SlangEntry]:
        """Search using regex pattern (term or definition)"""
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        results = []
        for entry in self.db.entries:
            if compiled.search(entry.term) or compiled.search(entry.definition):
                results.append(entry)
        return results

    def semantic_search_placeholder(self, query: str, limit: int = 5) -> List[SlangEntry]:
        """
        PLACEHOLDER for future vector/semantic search.
        Currently just returns random related terms.
        """
        # In future: use sentence-transformers to find semantically similar definitions
        fuzzy_results = self.fuzzy_search(query, threshold=0.3, limit=50)
        if fuzzy_results:
            # Return top by popularity among fuzzy matches
            entries = [entry for entry, score in fuzzy_results]
            entries.sort(key=lambda x: x.popularity_score, reverse=True)
            return entries[:limit]
        else:
            # Fallback to random
            return self.db.random(limit)

    def search_with_filter(self, query: str, slang_filter: SlangFilter, fuzzy_threshold: float = 0.0) -> List[SlangEntry]:
        """Combine fuzzy search with SlangFilter"""
        # First apply filter
        filtered = self.db.search(slang_filter)

        if not query.strip():
            return filtered[:10]

        # Then apply fuzzy on filtered set
        query_lower = query.lower().strip()
        scored = [
            (entry, self._calculate_similarity(query_lower, entry.term.lower()))
            for entry in filtered
        ]
        scored = [item for item in scored if item[1] >= fuzzy_threshold]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [entry for entry, score in scored]

    def get_similar_terms(self, term: str, limit: int = 5) -> List[SlangEntry]:
        """Get terms similar to given term (via related_terms or fuzzy)"""
        entry = self.db.get(term)
        if entry and entry.related_terms:
            related_entries = [self.db.get(rt) for rt in entry.related_terms if self.db.get(rt)]
            return [e for e in related_entries if e][:limit]

        # Fallback to fuzzy
        fuzzy_results = self.fuzzy_search(term, threshold=0.4, limit=limit+5)
        return [entry for entry, score in fuzzy_results if entry.term.lower() != term.lower()][:limit]
