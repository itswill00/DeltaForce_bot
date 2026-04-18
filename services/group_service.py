from database.json_manager import DeltaJSONDB, db_manager
from datetime import datetime

class GroupDTO:
    def __init__(self, chat_id: int, data: dict):
        self.id = chat_id
        self.title = data.get("title")
        self.settings = data.get("settings", {
            "auto_intel": False,
            "trivia_enabled": True,
            "auto_cleanup": True,
            "last_intel_post": ""
        })
        self.members = data.get("members", [])
        self.created_at = data.get("created_at")

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, item):
        return getattr(self, item)

class GroupService:
    def __init__(self, db: DeltaJSONDB = db_manager):
        self.db = db

    async def get_group(self, chat_id: int) -> GroupDTO:
        data = await self.db.get_all()
        g_data = data["groups"].get(str(chat_id))
        return GroupDTO(chat_id, g_data) if g_data else None

    async def register_group(self, chat_id: int, title: str):
        data = await self.db.get_all()
        cid = str(chat_id)
        if cid not in data["groups"]:
            data["groups"][cid] = {
                "title": title,
                "created_at": datetime.now().isoformat(),
                "settings": {
                    "auto_intel": False,
                    "trivia_enabled": True,
                    "auto_cleanup": True,
                    "last_intel_post": ""
                },
                "members": []
            }
        else:
            data["groups"][cid]["title"] = title
        await self.db.save(data)
        return GroupDTO(chat_id, data["groups"][cid])

    async def update_settings(self, chat_id: int, key: str, value):
        data = await self.db.get_all()
        cid = str(chat_id)
        if cid in data["groups"]:
            data["groups"][cid]["settings"][key] = value
            await self.db.save(data)

    async def track_member(self, chat_id: int, user_id: int):
        data = await self.db.get_all()
        cid = str(chat_id)
        if cid in data["groups"]:
            if user_id not in data["groups"][cid]["members"]:
                data["groups"][cid]["members"].append(user_id)
                await self.db.save(data)

    async def get_active_intel_groups(self):
        data = await self.db.get_all()
        active = []
        for cid, info in data["groups"].items():
            if info.get("settings", {}).get("auto_intel", False):
                active.append(int(cid))
        return active
