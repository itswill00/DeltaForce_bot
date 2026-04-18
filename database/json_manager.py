import json
import os
import asyncio
import aiofiles
import logging
from config import settings

class DeltaJSONDB:
    """Enterprise-grade JSON persistence with atomic replacement and in-memory caching."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lock = asyncio.Lock()
        self._cache = {
            "users": {},
            "groups": {},
            "lfg": {}
        }
        self._load_from_disk()

    def _load_from_disk(self):
        """Initial load from file on startup."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=4)
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure structure matches
                for key in self._cache:
                    if key not in data:
                        data[key] = {}
                self._cache = data
        except (json.JSONDecodeError, FileNotFoundError):
            logging.error(f"Corruption detected in {self.file_path}. Initializing empty DB.")

    async def get_all(self):
        """Read state from memory (O(1))."""
        async with self.lock:
            return self._cache

    async def save(self, data: dict):
        """Update cache and write to disk atomically."""
        async with self.lock:
            self._cache = data
            temp_file = self.file_path + ".tmp"
            try:
                # Write to temp file first
                async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(data, indent=4, ensure_ascii=False))
                
                # Atomic replace: original file is only replaced if write succeeds
                os.replace(temp_file, self.file_path)
            except Exception as e:
                logging.error(f"JSON Write Failure: {e}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)

# Global Instance
db_manager = DeltaJSONDB(settings.local_db_path)
