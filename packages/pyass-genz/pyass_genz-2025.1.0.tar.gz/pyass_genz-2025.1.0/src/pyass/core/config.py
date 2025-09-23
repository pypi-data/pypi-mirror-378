# pyass🍑/src/pyass/core/config.py

import os
import json
import importlib.resources as resources

class PyAssConfig:
    """
    Global configuration for pyass🍑 behavior.
    Can be overridden by env vars or user config file.
    """

    def __init__(self):
        # Defaults
        self.default_region: str = os.getenv("PYASS_REGION", "GLOBAL")
        self.default_platform: str = os.getenv("PYASS_PLATFORM", "TikTok")
        self.enable_emojis: bool = os.getenv("PYASS_EMOJIS", "1").lower() in ("1", "true", "yes")
        self.safe_mode: bool = os.getenv("PYASS_SAFE", "0").lower() in ("1", "true", "yes")
        self.cache_size: int = int(os.getenv("PYASS_CACHE_SIZE", "1000"))
        self.data_path: str = os.getenv("PYASS_DATA_PATH", "src/pyass/data/base_slang.json")

        # Load user config if exists
        self._load_user_config()

    def _load_user_config(self):
        """Load ~/.pyass/config.json if exists"""
        config_path = os.path.expanduser("~/.pyass/config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    for key, value in user_config.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception:
                pass  # Silently fail — defaults are safe

    def save_user_config(self):
        """Save current config to ~/.pyass/config.json"""
        config_path = os.path.expanduser("~/.pyass/config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        config_dict = {
            "default_region": self.default_region,
            "default_platform": self.default_platform,
            "enable_emojis": self.enable_emojis,
            "safe_mode": self.safe_mode,
            "cache_size": self.cache_size,
            "data_path": self.data_path
        }

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2)

    def get_data_path(self) -> str:
        """Get the path to the default slang data file within the package"""
        try:
            # Use importlib.resources for Python 3.9+
            data_path = resources.files("pyass.data") / "base_slang.json"
            return str(data_path)
        except AttributeError:
            # Fallback for older Python versions
            import pyass.data
            return os.path.join(os.path.dirname(pyass.data.__file__), "base_slang.json")

    @classmethod
    def get(cls):
        """Singleton-like access"""
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
