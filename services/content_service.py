import json
import os
from database.json_manager import DeltaJSONDB, db_manager

class ContentService:
    def __init__(self, db: DeltaJSONDB = db_manager):
        self.db = db

    async def _initialize_if_empty(self):
        """Seed DB from static JSON files if DB content is empty."""
        data = await self.db.get_all()
        if not data["content"]["weapons"]:
            try:
                with open("data/loadout.json", "r", encoding="utf-8") as f:
                    data["content"]["weapons"] = json.load(f).get("senjata", {})
            except Exception: pass
            
        if not data["content"]["maps"]:
            try:
                with open("data/maps.json", "r", encoding="utf-8") as f:
                    data["content"]["maps"] = json.load(f)
            except Exception: pass
        await self.db.save(data)

    async def get_weapons(self):
        await self._initialize_if_empty()
        data = await self.db.get_all()
        return data["content"]["weapons"]

    async def update_weapon(self, weapon_id: str, weapon_data: dict):
        data = await self.db.get_all()
        data["content"]["weapons"][weapon_id] = weapon_data
        await self.db.save(data)

    async def delete_weapon(self, weapon_id: str):
        data = await self.db.get_all()
        if weapon_id in data["content"]["weapons"]:
            del data["content"]["weapons"][weapon_id]
            await self.db.save(data)

    async def get_maps(self):
        await self._initialize_if_empty()
        data = await self.db.get_all()
        return data["content"]["maps"]

    async def update_map(self, map_id: str, map_data: dict):
        data = await self.db.get_all()
        data["content"]["maps"][map_id] = map_data
        await self.db.save(data)
