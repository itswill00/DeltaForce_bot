from database.json_manager import DeltaJSONDB, db_manager
import uuid
import time
from services.user_service import UserService

class SessionDTO:
    def __init__(self, session_id: str, data: dict):
        self.id = session_id
        self.host_id = data.get("host_id")
        self.host_name = data.get("host_name")
        self.lfg_type = data.get("lfg_type")
        self.max_players = data.get("max_players")
        self.players = data.get("players", [])
        self.status = data.get("status", "open")
        self.timestamp = data.get("timestamp", time.time())

    def get(self, key, default=None):
        return getattr(self, key, default)

class LfgService:
    def __init__(self, db: DeltaJSONDB = db_manager):
        self.db = db
        self.user_service = UserService(db)

    async def get_session(self, session_id: str) -> SessionDTO:
        data = await self.db.get_all()
        s_data = data["lfg"].get(session_id)
        return SessionDTO(session_id, s_data) if s_data else None

    async def get_all_sessions(self):
        data = await self.db.get_all()
        return {sid: SessionDTO(sid, s) for sid, s in data["lfg"].items()}

    async def create_session(self, host_id: int, host_name: str, lfg_type: str, max_players: int):
        data = await self.db.get_all()
        session_id = str(uuid.uuid4())[:8]
        new_session = {
            "host_id": host_id,
            "host_name": host_name,
            "lfg_type": lfg_type,
            "max_players": max_players,
            "players": [host_id],
            "status": "open",
            "timestamp": time.time()
        }
        data["lfg"][session_id] = new_session
        await self.db.save(data)
        return SessionDTO(session_id, new_session)

    async def join_session(self, session_id: str, user_id: int):
        data = await self.db.get_all()
        if session_id not in data["lfg"]: return None, "Sesi tidak ditemukan."
        
        lfg = data["lfg"][session_id]
        if lfg["status"] != "open": return None, "Sesi sudah ditutup."
        if user_id in lfg["players"]: return None, "Anda sudah di dalam skuad."
        if len(lfg["players"]) >= lfg["max_players"]: return None, "Skuad sudah penuh."
        
        lfg["players"].append(user_id)
        
        if len(lfg["players"]) == lfg["max_players"]:
            lfg["status"] = "closed"
            for pid in lfg["players"]:
                uid = str(pid)
                if uid in data["users"]:
                    data["users"][uid]["mabar_score"] = data["users"][uid].get("mabar_score", 0) + 1
                    data["users"][uid]["xp"] = data["users"][uid].get("xp", 0) + 25
        
        await self.db.save(data)
        return SessionDTO(session_id, lfg), "Berhasil bergabung."

    async def leave_session(self, session_id: str, user_id: int):
        data = await self.db.get_all()
        if session_id not in data["lfg"]: return None, "Sesi tidak ditemukan."
        
        lfg = data["lfg"][session_id]
        if user_id == lfg["host_id"]:
            lfg["status"] = "closed"
            await self.db.save(data)
            return SessionDTO(session_id, lfg), "Sesi dibatalkan oleh Host."
            
        if user_id not in lfg["players"]: return None, "Anda tidak di dalam skuad."
        
        lfg["players"].remove(user_id)
        await self.db.save(data)
        return SessionDTO(session_id, lfg), "Berhasil keluar."

    async def delete_session(self, session_id: str):
        data = await self.db.get_all()
        if session_id in data["lfg"]:
            del data["lfg"][session_id]
            await self.db.save(data)
            return True
        return False
