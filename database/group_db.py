import os
import logging
from datetime import datetime
from database.json_manager import AsyncJSONManager
from config import settings

class GroupDB:
    """Handles Group metadata, member lists, and specific settings."""
    def __init__(self):
        self.db = AsyncJSONManager(settings.group_path, default_data={})

    async def register_group(self, chat_id: int, title: str):
        """Register or update group info when bot interacts with it."""
        data = await self.db.read()
        cid = str(chat_id)
        if cid not in data:
            data[cid] = {
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
            data[cid]["title"] = title
            
        await self.db.write(data)

    async def update_settings(self, chat_id: int, setting_key: str, value):
        data = await self.db.read()
        cid = str(chat_id)
        if cid not in data: return
        data[cid]["settings"][setting_key] = value
        await self.db.write(data)

    async def track_member(self, chat_id: int, user_id: int):
        """Add a user to the group's internal member list for local leaderboards."""
        data = await self.db.read()
        cid = str(chat_id)
        if cid not in data: return
        
        if user_id not in data[cid]["members"]:
            data[cid]["members"].append(user_id)
            await self.db.write(data)

    async def get_group(self, chat_id: int):
        data = await self.db.read()
        return data.get(str(chat_id))

    async def get_active_intel_groups(self):
        """Returns list of chat IDs where auto_intel is enabled."""
        data = await self.db.read()
        active = []
        for cid, info in data.items():
            if info.get("settings", {}).get("auto_intel", False):
                active.append(int(cid))
        return active

# Global instance
group_db = GroupDB()
