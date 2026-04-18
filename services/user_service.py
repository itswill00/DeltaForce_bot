from database.json_manager import DeltaJSONDB, db_manager
import math
from datetime import datetime

class UserDTO:
    """A data object to simulate SQLAlchemy-like objects for the JSON layer."""
    def __init__(self, user_id: int, data: dict):
        self.id = user_id
        self.ign = data.get("ign")
        self.role = data.get("role")
        self.level = data.get("level", 1)
        self.xp = data.get("xp", 0)
        self.rep_points = data.get("rep_points", 0)
        self.mabar_score = data.get("mabar_score", 0)
        self.balance = data.get("balance", 0)
        self.last_login = data.get("last_login")
        self.is_admin = data.get("is_admin", False)
        self.owned_items = data.get("owned_items", [])

class UserService:
    def __init__(self, db: DeltaJSONDB = db_manager):
        self.db = db

    async def get_user(self, user_id: int) -> UserDTO:
        data = await self.db.get_all()
        user_data = data["users"].get(str(user_id))
        return UserDTO(user_id, user_data) if user_data else None

    async def register_user(self, user_id: int, ign: str, role: str, first_name: str, username: str):
        data = await self.db.get_all()
        uid = str(user_id)
        if uid not in data["users"]:
            data["users"][uid] = {
                "level": 1, "xp": 0, "rep_points": 0, "mabar_score": 0,
                "balance": 0, "owned_items": [], "is_admin": False
            }
        
        data["users"][uid].update({
            "ign": ign,
            "role": role,
            "first_name": first_name,
            "username": username
        })
        await self.db.save(data)
        return UserDTO(user_id, data["users"][uid])

    async def add_xp(self, user_id: int, amount: int):
        data = await self.db.get_all()
        uid = str(user_id)
        if uid not in data["users"]: return
        
        user = data["users"][uid]
        user["xp"] = user.get("xp", 0) + amount
        
        # Enterprise Formula
        new_level = int(math.sqrt(user["xp"] / 25)) + 1
        user["level"] = new_level
        
        await self.db.save(data)

    async def add_rep(self, user_id: int, amount: int = 1):
        data = await self.db.get_all()
        uid = str(user_id)
        if uid in data["users"]:
            data["users"][uid]["rep_points"] = data["users"][uid].get("rep_points", 0) + amount
            await self.db.save(data)

    async def get_top_players(self, limit: int = 10, category: str = "mabar_score"):
        data = await self.db.get_all()
        sorted_users = sorted(
            [UserDTO(int(uid), u) for uid, u in data["users"].items() if category in u],
            key=lambda x: getattr(x, category, 0),
            reverse=True
        )
        return sorted_users[:limit]

    async def update_last_login(self, user_id: int):
        data = await self.db.get_all()
        uid = str(user_id)
        if uid in data["users"]:
            data["users"][uid]["last_login"] = datetime.now().date().isoformat()
            await self.db.save(data)
