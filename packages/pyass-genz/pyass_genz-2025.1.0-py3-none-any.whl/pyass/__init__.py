# pyass🍑/src/pyass/__init__.py

__version__ = "2025.1.0"

__all__ = [
    # Core classes
    "SlangEntry",
    "SlangFilter",
    "SlangDB",
    "get_slang_db",
    "PyAssConfig",

    # Engines
    "Translator",
    "MoodEngine",
    "Quizzer",
    "SlangSearchEngine",

    # CLI
    "app",  # Main CLI app

    # API
    "PyAssAsyncClient",
    "get_client",
]

# Core imports
from .core.models import SlangEntry, SlangFilter
from .core.slangdb import SlangDB, get_slang_db
from .core.config import PyAssConfig

# Engine imports
from .engines.translator import Translator
from .engines.mood_engine import MoodEngine
from .engines.quizzer import Quizzer
from .engines.search import SlangSearchEngine

# CLI imports
from .cli.commands import app

# API imports
from .api.async_client import PyAssAsyncClient, get_client
