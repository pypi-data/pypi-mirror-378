# pyass🍑/src/pyass/utils/metrics.py

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import atexit

class SlangMetrics:
    """
    Track usage, slang IQ history, performance stats.
    Persists to ~/.pyass/metrics.json
    """

    def __init__(self):
        self.metrics_file = Path.home() / ".pyass" / "metrics.json"
        self.data = self._load_metrics()
        atexit.register(self.save)  # Auto-save on exit

    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file or return defaults"""
        if not self.metrics_file.exists():
            return self._default_metrics()

        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._default_metrics()

    def _default_metrics(self) -> Dict[str, Any]:
        return {
            "first_use": datetime.now().isoformat(),
            "last_use": datetime.now().isoformat(),
            "total_lookups": 0,
            "total_translations": 0,
            "quiz_scores": [],
            "favorite_terms": {},
            "persona_usage": {},
            "platform_usage": {},
            "session_count": 0,
            "version_history": []
        }

    def save(self):
        """Save metrics to disk"""
        try:
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Fail silently

    def record_lookup(self, term: str, success: bool = True):
        """Record a slang lookup"""
        self.data["total_lookups"] += 1
        self.data["last_use"] = datetime.now().isoformat()

        if success:
            self.data["favorite_terms"][term] = self.data["favorite_terms"].get(term, 0) + 1

    def record_translation(self, original: str, translated: str):
        """Record a translation"""
        self.data["total_translations"] += 1
        self.data["last_use"] = datetime.now().isoformat()

    def record_quiz_score(self, score: int, total: int, slang_iq: int):
        """Record quiz result"""
        self.data["quiz_scores"].append({
            "date": datetime.now().isoformat(),
            "score": score,
            "total": total,
            "slang_iq": slang_iq
        })

    def record_persona_usage(self, persona: str):
        """Record persona usage"""
        self.data["persona_usage"][persona] = self.data["persona_usage"].get(persona, 0) + 1

    def record_platform_usage(self, platform: str):
        """Record platform usage"""
        self.data["platform_usage"][platform] = self.data["platform_usage"].get(platform, 0) + 1

    def start_session(self):
        """Record new session"""
        self.data["session_count"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get current stats"""
        return {
            "total_lookups": self.data["total_lookups"],
            "total_translations": self.data["total_translations"],
            "quiz_count": len(self.data["quiz_scores"]),
            "session_count": self.data["session_count"],
            "top_terms": sorted(
                self.data["favorite_terms"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "top_personas": sorted(
                self.data["persona_usage"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "avg_slang_iq": (
                sum(q["slang_iq"] for q in self.data["quiz_scores"]) / len(self.data["quiz_scores"])
                if self.data["quiz_scores"] else 0
            )
        }

    def reset(self):
        """Reset all metrics"""
        self.data = self._default_metrics()
        self.save()

# Global metrics instance
GLOBAL_METRICS = SlangMetrics()

# Convenience functions
def record_lookup(term: str, success: bool = True):
    GLOBAL_METRICS.record_lookup(term, success)

def record_translation(original: str, translated: str):
    GLOBAL_METRICS.record_translation(original, translated)

def record_quiz_score(score: int, total: int, slang_iq: int):
    GLOBAL_METRICS.record_quiz_score(score, total, slang_iq)

def record_persona_usage(persona: str):
    GLOBAL_METRICS.record_persona_usage(persona)

def record_platform_usage(platform: str):
    GLOBAL_METRICS.record_platform_usage(platform)

def start_session():
    GLOBAL_METRICS.start_session()

def get_stats() -> Dict[str, Any]:
    return GLOBAL_METRICS.get_stats()
