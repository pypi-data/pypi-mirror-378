# pyass🍑/src/pyass/utils/updater.py

import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import urllib.request
import hashlib
from datetime import datetime

from ..core.config import PyAssConfig

class SlangUpdater:
    """
    Auto-update slang database from CDN/community source.
    Checks versions, downloads, verifies checksums.
    """

    # In real life, this would point to your CDN or GitHub releases
    CDN_BASE_URL = "https://raw.githubusercontent.com/yourusername/pyass-peach/main/data/"
    MANIFEST_URL = CDN_BASE_URL + "manifest.json"
    DEFAULT_DATA_FILE = "base_slang.json"

    def __init__(self):
        self.config = PyAssConfig.get()
        self.local_data_path = Path(self.config.data_path)
        self.local_manifest_path = self.local_data_path.parent / "manifest.json"
        self.backup_dir = self.local_data_path.parent / "backups"

    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """Check if a new version is available"""
        try:
            with urllib.request.urlopen(self.MANIFEST_URL, timeout=10) as response:
                remote_manifest = json.loads(response.read().decode('utf-8'))

            local_version = self._get_local_version()
            if local_version is None or remote_manifest["version"] > local_version:
                return remote_manifest
            else:
                return None
        except Exception as e:
            print(f"⚠️  Failed to check for updates: {e}")
            return None

    def _get_local_version(self) -> Optional[str]:
        """Get local manifest version"""
        if not self.local_manifest_path.exists():
            return None
        try:
            with open(self.local_manifest_path, 'r', encoding='utf-8') as f:
                local_manifest = json.load(f)
                return local_manifest.get("version")
        except Exception:
            return None

    def update(self, force: bool = False) -> bool:
        """Perform update if new version available"""
        if not force:
            remote_manifest = self.check_for_updates()
            if not remote_manifest:
                print("✅ No updates available")
                return False
        else:
            # Force update — refetch manifest
            try:
                with urllib.request.urlopen(self.MANIFEST_URL, timeout=10) as response:
                    remote_manifest = json.loads(response.read().decode('utf-8'))
            except Exception as e:
                print(f"⚠️  Failed to fetch manifest: {e}")
                return False

        print(f"⬇️  Updating to version {remote_manifest['version']}...")

        # Backup current
        self._backup_current()

        # Download new data file
        data_url = self.CDN_BASE_URL + remote_manifest["file"]
        temp_file = self.local_data_path.parent / f"{self.DEFAULT_DATA_FILE}.tmp"

        try:
            urllib.request.urlretrieve(data_url, temp_file)

            # Verify checksum
            if remote_manifest.get("sha256"):
                if self._calculate_sha256(temp_file) != remote_manifest["sha256"]:
                    raise ValueError("Checksum mismatch — corrupted download")

            # Replace current
            shutil.move(temp_file, self.local_data_path)

            # Save new manifest
            with open(self.local_manifest_path, 'w', encoding='utf-8') as f:
                json.dump(remote_manifest, f, indent=2)

            print(f"🎉 Successfully updated to {remote_manifest['version']}")
            return True

        except Exception as e:
            print(f"❌ Update failed: {e}")
            # Restore backup
            self._restore_backup()
            return False

    def _backup_current(self):
        """Backup current data and manifest"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.local_data_path.exists():
            shutil.copy2(
                self.local_data_path,
                self.backup_dir / f"base_slang_{timestamp}.json"
            )

        if self.local_manifest_path.exists():
            shutil.copy2(
                self.local_manifest_path,
                self.backup_dir / f"manifest_{timestamp}.json"
            )

    def _restore_backup(self):
        """Restore latest backup"""
        backups = sorted(self.backup_dir.glob("base_slang_*.json"), reverse=True)
        if backups:
            latest = backups[0]
            shutil.copy2(latest, self.local_data_path)
            print(f"🔄 Restored from backup: {latest.name}")

    def _calculate_sha256(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_update_info(self) -> Dict[str, Any]:
        """Get info about available update"""
        remote = self.check_for_updates()
        local_version = self._get_local_version()

        return {
            "current_version": local_version or "unknown",
            "latest_version": remote["version"] if remote else local_version,
            "update_available": remote is not None,
            "changelog": remote.get("changelog", []) if remote else [],
            "release_date": remote.get("release_date") if remote else None
        }

# Convenience function
def update_slang_db(force: bool = False) -> bool:
    """Update slang database"""
    updater = SlangUpdater()
    return updater.update(force=force)

def check_for_updates() -> Dict[str, Any]:
    """Check for updates"""
    updater = SlangUpdater()
    return updater.get_update_info()
