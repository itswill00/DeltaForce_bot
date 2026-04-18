from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import LFGSession, User
from services.user_service import UserService
import uuid

class LfgService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session)

    async def get_session(self, session_id: str) -> LFGSession:
        result = await self.session.execute(select(LFGSession).where(LFGSession.id == session_id))
        return result.scalar_one_or_none()

    async def create_session(self, host_id: int, host_name: str, lfg_type: str, max_players: int):
        session_id = str(uuid.uuid4())[:8]
        new_session = LFGSession(
            id=session_id,
            host_id=host_id,
            host_name=host_name,
            lfg_type=lfg_type,
            max_players=max_players,
            players=[host_id],
            status="open"
        )
        self.session.add(new_session)
        await self.session.commit()
        return new_session

    async def join_session(self, session_id: str, user_id: int):
        lfg = await self.get_session(session_id)
        if not lfg: return None, "Sesi tidak ditemukan."
        
        if lfg.status != "open": return None, "Sesi sudah ditutup."
        if user_id in lfg.players: return None, "Anda sudah di dalam skuad."
        if len(lfg.players) >= lfg.max_players: return None, "Skuad sudah penuh."
        
        # SQLAlchemy note: Since players is a JSON list, we need to create a new list 
        # for it to detect the change for the commit
        new_players = list(lfg.players)
        new_players.append(user_id)
        lfg.players = new_players
        
        # Check if full
        if len(lfg.players) == lfg.max_players:
            lfg.status = "closed"
            # Award points to all
            for pid in lfg.players:
                # We use the existing user_service here (same session)
                user = await self.user_service.get_user(pid)
                if user:
                    user.mabar_score += 1
                    user.xp += 25
        
        await self.session.commit()
        return lfg, "Berhasil bergabung."

    async def leave_session(self, session_id: str, user_id: int):
        lfg = await self.get_session(session_id)
        if not lfg: return None, "Sesi tidak ditemukan."
        
        if user_id == lfg.host_id:
            lfg.status = "closed"
            await self.session.commit()
            return lfg, "Sesi dibatalkan oleh Host."
            
        if user_id not in lfg.players: return None, "Anda tidak di dalam skuad."
        
        new_players = list(lfg.players)
        new_players.remove(user_id)
        lfg.players = new_players
        
        await self.session.commit()
        return lfg, "Berhasil keluar."

    async def delete_expired_sessions(self):
        # Implementation for garbage collection
        pass
