import os
import json
from database.json_manager import AsyncJSONManager
from config import settings
from jsonschema import validate, ValidationError
from pathlib import Path

# Load schema once
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "lfg_schema.json"
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    LFG_SCHEMA = json.load(f)

class LFGDB:
    """Handles active Mabar/LFG sessions via JSON."""
    def __init__(self):
        self.db = AsyncJSONManager(settings.lfg_path, default_data={})

    async def get_session(self, session_id: str):
        data = await self.db.read()
        return data.get(session_id)

    async def update_session(self, session_id: str, session_data: dict):
        # Validate against schema before saving
        try:
            # We validate the whole DB structure since AsyncJSONManager writes the whole thing
            data = await self.db.read()
            temp_data = data.copy()
            temp_data[session_id] = session_data
            validate(instance=temp_data, schema=LFG_SCHEMA)
            
            await self.db.write(temp_data)
        except ValidationError as e:
            import logging
            logging.error(f"LFG Validation Error for session {session_id}: {e.message}")
            raise ValueError(f"Invalid LFG data: {e.message}")
        
    async def delete_session(self, session_id: str):
        data = await self.db.read()
        if session_id in data:
            del data[session_id]
            await self.db.write(data)

# Global instance
lfg_db = LFGDB()
