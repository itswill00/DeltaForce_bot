from database.json_manager import DeltaJSONDB, db_manager

class SecurityService:
    def __init__(self, db: DeltaJSONDB = db_manager):
        self.db = db

    async def get_blacklist(self):
        data = await self.db.get_all()
        return data["system"].get("blacklist", [])

    async def add_to_blacklist(self, word: str):
        data = await self.db.get_all()
        blacklist = data["system"].get("blacklist", [])
        if word.lower() not in blacklist:
            blacklist.append(word.lower())
            data["system"]["blacklist"] = blacklist
            await self.db.save(data)
            return True
        return False

    async def remove_from_blacklist(self, word: str):
        data = await self.db.get_all()
        blacklist = data["system"].get("blacklist", [])
        if word.lower() in blacklist:
            blacklist.remove(word.lower())
            data["system"]["blacklist"] = blacklist
            await self.db.save(data)
            return True
        return False

    async def check_content(self, text: str):
        """Returns True if text contains blacklisted words."""
        blacklist = await self.get_blacklist()
        text_lower = text.lower()
        for word in blacklist:
            if word in text_lower:
                return True
        return False
