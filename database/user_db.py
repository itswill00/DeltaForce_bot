import os
from database.json_manager import AsyncJSONManager
from config import settings

class UserDB:
    """Handles User Profiles (In-game ID, Roles, Stats) via JSON."""
    def __init__(self):
        self.db = AsyncJSONManager(settings.user_path, default_data={})

    async def get_user(self, user_id: int):
        data = await self.db.read()
        return data.get(str(user_id))

    async def update_user(self, user_id: int, user_data: dict):
        data = await self.db.read()
        str_id = str(user_id)
        if str_id not in data:
            data[str_id] = {
                "xp": 0,
                "rep_points": 0,
                "mabar_score": 0,
                "trivia_score": 0,
                "balance": 0,
                "level": 1,
                "last_login": ""
            }
        data[str_id].update(user_data)
        await self.db.write(data)

    async def get_all_users(self):
        return await self.db.read()

    async def increment_mabar_score(self, user_id: int):
        await self.add_xp(user_id, 25) # Mabar gives 25 XP
        data = await self.db.read()
        str_id = str(user_id)
        if str_id not in data: return
        data[str_id]["mabar_score"] = data[str_id].get("mabar_score", 0) + 1
        await self.db.write(data)
        
    async def increment_trivia_score(self, user_id: int, points: int = 5):
        await self.add_xp(user_id, points * 2) # Trivia points give 2x XP
        data = await self.db.read()
        str_id = str(user_id)
        if str_id not in data: return
        data[str_id]["trivia_score"] = data[str_id].get("trivia_score", 0) + points
        await self.db.write(data)

    async def add_xp(self, user_id: int, amount: int):
        data = await self.db.read()
        str_id = str(user_id)
        if str_id not in data: return
        
        old_xp = data[str_id].get("xp", 0)
        new_xp = old_xp + amount
        data[str_id]["xp"] = new_xp
        
        # Calculate level: Level 1 @ 0 XP, Level 2 @ 100 XP, Level 3 @ 300 XP, Level 4 @ 600 XP ...
        # Formula: level = floor(sqrt(xp/50)) + 1 approximately
        import math
        new_level = int(math.sqrt(new_xp / 25)) + 1
        data[str_id]["level"] = new_level
        
        await self.db.write(data)

    async def add_rep(self, user_id: int, amount: int = 1):
        data = await self.db.read()
        str_id = str(user_id)
        if str_id not in data: return
        data[str_id]["rep_points"] = data[str_id].get("rep_points", 0) + amount
        await self.db.write(data)

    async def add_balance(self, user_id: int, amount: int):
        data = await self.db.read()
        str_id = str(user_id)
        if str_id not in data: return
        data[str_id]["balance"] = data[str_id].get("balance", 0) + amount
        await self.db.write(data)

    async def get_top_players(self, limit: int = 10, category: str = "mabar_score"):
        data = await self.db.read()
        sorted_users = sorted(
            [u for u in data.values() if category in u],
            key=lambda x: x[category],
            reverse=True
        )
        return sorted_users[:limit]

    async def get_users_by_role(self, role: str):
        data = await self.db.read()
        return [int(str_id) for str_id, u in data.items() if u.get("role") == role]

    async def get_user_count(self):
        data = await self.db.read()
        return len(data)

    async def set_admin_status(self, user_id: int, is_admin: bool):
        data = await self.db.read()
        str_id = str(user_id)
        if str_id not in data:
            data[str_id] = {}
            
        if is_admin:
            data[str_id]["is_admin"] = True
        else:
            if "is_admin" in data[str_id]:
                del data[str_id]["is_admin"]
                
        await self.db.write(data)

    async def is_user_admin(self, user_id: int):
        data = await self.db.read()
        user_info = data.get(str(user_id), {})
        return user_info.get("is_admin", False)

    async def update_last_login(self, user_id: int, date_str: str):
        data = await self.db.read()
        str_id = str(user_id)
        if str_id not in data: return
        data[str_id]["last_login"] = date_str
        await self.db.write(data)

# Global instance
user_db = UserDB()
