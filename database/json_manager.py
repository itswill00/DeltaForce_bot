import json
import os
import asyncio
import aiofiles
import logging

class AsyncJSONManager:
    """A wrapper for concurrent-safe JSON read/write operations using in-memory cache and atomic file writes."""
    
    def __init__(self, file_path: str, default_data=None):
        self.file_path = file_path
        self.lock = asyncio.Lock()
        self.default_data = default_data if default_data is not None else {}
        self._cache = None
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure the JSON file exists, create with default data if not, and load to cache."""
        dir_name = os.path.dirname(self.file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_data, f, indent=4)
                
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._cache = self.default_data.copy()

    async def read(self):
        """Read data from in-memory cache (O(1) complexity, Extremely Fast)."""
        async with self.lock:
            return self._cache

    async def write(self, data):
        """Update cache and write to disk safely using Atomic Replacement."""
        async with self.lock:
            self._cache = data
            temp_file = self.file_path + ".tmp"
            try:
                async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(data, indent=4, ensure_ascii=False))
                # Atomic replace ensures if bot crashes during write, original file is safe
                os.replace(temp_file, self.file_path)
            except Exception as e:
                logging.error(f"Failed to write JSON {self.file_path}: {e}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
