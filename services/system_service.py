from database.json_manager import DeltaJSONDB, db_manager
import logging

class SystemService:
    def __init__(self, db: DeltaJSONDB = db_manager):
        self.db = db

    async def get_settings(self):
        data = await self.db.get_all()
        return data.get("system", {"maintenance": False, "event_multiplier": 1.0})

    async def update_setting(self, key: str, value):
        data = await self.db.get_all()
        if "system" not in data:
            data["system"] = {"maintenance": False, "event_multiplier": 1.0}
        data["system"][key] = value
        await self.db.save(data)

    async def toggle_maintenance(self):
        settings = await self.get_settings()
        new_val = not settings.get("maintenance", False)
        await self.update_setting("maintenance", new_val)
        return new_val

    async def set_event_multiplier(self, multiplier: float):
        await self.update_setting("event_multiplier", multiplier)

    async def mass_reward(self, coin_amount: int = 0, xp_amount: int = 0):
        """Injects coins or XP into every registered user's account."""
        data = await self.db.get_all()
        users = data.get("users", {})
        count = 0
        for uid in users:
            if xp_amount > 0:
                users[uid]["xp"] = users[uid].get("xp", 0) + xp_amount
            if coin_amount > 0:
                users[uid]["balance"] = users[uid].get("balance", 0) + coin_amount
            count += 1
        await self.db.save(data)
        return count

    async def get_banner(self, banner_key: str):
        """Returns banner URL from DB or falls back to config."""
        from config import settings
        data = await self.db.get_all()
        banners = data["system"].get("banners", {})
        
        # Fallback logic
        db_banner = banners.get(banner_key)
        if db_banner: return db_banner
        
        return getattr(settings, f"banner_{banner_key}", settings.banner_main)

    async def set_banner(self, banner_key: str, url: str):
        """Updates a specific banner URL in DB."""
        data = await self.db.get_all()
        if "banners" not in data["system"]: data["system"]["banners"] = {}
        data["system"]["banners"][banner_key] = url
        await self.db.save(data)
