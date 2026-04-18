import json
import os
from database.json_manager import DeltaJSONDB, db_manager

class ContentService:
    def __init__(self, db: DeltaJSONDB = db_manager):
        self.db = db

    async def _initialize_if_empty(self):
        """Seed DB from static JSON files with robust structure checks."""
        data = await self.db.get_all()
        
        # Ensure content structure exists
        if "content" not in data:
            data["content"] = {"weapons": {}, "maps": {}, "shop": {}}
        elif "shop" not in data["content"]:
            data["content"]["shop"] = {}

        changed = False
        if not data["content"].get("weapons"):
            try:
                if os.path.exists("data/loadout.json"):
                    with open("data/loadout.json", "r", encoding="utf-8") as f:
                        data["content"]["weapons"] = json.load(f).get("senjata", {})
                        changed = True
            except Exception: pass
            
        if not data["content"].get("maps"):
            try:
                if os.path.exists("data/maps.json"):
                    with open("data/maps.json", "r", encoding="utf-8") as f:
                        data["content"]["maps"] = json.load(f)
                        changed = True
            except Exception: pass
            
        if not data["content"].get("shop"):
            # Default Seed for Dynamic Economy
            data["content"]["shop"] = {
                "flair_recon": {"name": "Elite Recon Badge", "price": 500, "type": "badge", "desc": "Tanda pengintai ahli."},
                "flair_medic": {"name": "Field Surgeon Badge", "price": 500, "type": "badge", "desc": "Tanda medis garis depan."},
                "flair_assault": {"name": "Vanguard Badge", "price": 500, "type": "badge", "desc": "Tanda pahlawan penyerang."},
                "flair_vet": {"name": "Season 1 Veteran", "price": 2000, "type": "badge", "desc": "Gelar pemain angkatan pertama."}
            }
            changed = True
            
        if changed:
            await self.db.save(data)

    async def get_weapons(self):
        await self._initialize_if_empty()
        data = await self.db.get_all()
        return data["content"].get("weapons", {})

    async def update_weapon(self, weapon_id: str, weapon_data: dict):
        data = await self.db.get_all()
        if "content" not in data: data["content"] = {"weapons": {}, "maps": {}, "shop": {}}
        data["content"]["weapons"][weapon_id] = weapon_data
        await self.db.save(data)

    async def delete_weapon(self, weapon_id: str):
        data = await self.db.get_all()
        if "content" in data and weapon_id in data["content"]["weapons"]:
            del data["content"]["weapons"][weapon_id]
            await self.db.save(data)

    async def get_maps(self):
        await self._initialize_if_empty()
        data = await self.db.get_all()
        return data["content"].get("maps", {})

    async def update_map(self, map_id: str, map_data: dict):
        data = await self.db.get_all()
        if "content" not in data: data["content"] = {"weapons": {}, "maps": {}, "shop": {}}
        data["content"]["maps"][map_id] = map_data
        await self.db.save(data)

    async def get_shop_items(self):
        await self._initialize_if_empty()
        data = await self.db.get_all()
        return data["content"].get("shop", {})

    async def update_shop_item(self, item_id: str, item_data: dict):
        data = await self.db.get_all()
        if "content" not in data: data["content"] = {"weapons": {}, "maps": {}, "shop": {}}
        if "shop" not in data["content"]: data["content"]["shop"] = {}
        data["content"]["shop"][item_id] = item_data
        await self.db.save(data)

    async def delete_shop_item(self, item_id: str):
        data = await self.db.get_all()
        if "content" in data and "shop" in data["content"] and item_id in data["content"]["shop"]:
            del data["content"]["shop"][item_id]
            await self.db.save(data)
