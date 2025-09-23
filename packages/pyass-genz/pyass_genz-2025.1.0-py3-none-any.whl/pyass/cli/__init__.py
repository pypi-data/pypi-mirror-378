# pyass🍑/src/pyass/cli/__init__.py

__all__ = [
    "app",
    "VibePrinter",
]

from .commands import app
from .theme import VibePrinter

# Expose app for setup.py entry_points
