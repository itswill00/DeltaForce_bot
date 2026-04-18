from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
import math
from datetime import datetime

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> User:
        """Retrieve user from DB or return None."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def register_user(self, user_id: int, ign: str, role: str, first_name: str, username: str):
        """Register a new user or update existing details."""
        user = await self.get_user(user_id)
        if not user:
            user = User(
                id=user_id,
                ign=ign,
                role=role,
                first_name=first_name,
                username=username,
                owned_items=[]
            )
            self.session.add(user)
        else:
            user.ign = ign
            user.role = role
            user.first_name = first_name
            user.username = username
        
        await self.session.commit()
        return user

    async def add_xp(self, user_id: int, amount: int):
        """Add XP and automatically calculate level-up."""
        user = await self.get_user(user_id)
        if not user: return
        
        user.xp += amount
        
        # Enterprise Leveling Formula: L = sqrt(XP/25) + 1
        new_level = int(math.sqrt(user.xp / 25)) + 1
        if new_level > user.level:
            user.level = new_level
            # Potential for level-up notifications here
            
        await self.session.commit()
        return user

    async def add_rep(self, user_id: int, amount: int = 1):
        user = await self.get_user(user_id)
        if user:
            user.rep_points += amount
            await self.session.commit()

    async def add_balance(self, user_id: int, amount: int):
        user = await self.get_user(user_id)
        if user:
            user.balance += amount
            await self.session.commit()

    async def get_top_players(self, limit: int = 10, category: str = "mabar_score"):
        """Get leaderboard with optimized DB sorting."""
        column = getattr(User, category, User.mabar_score)
        query = select(User).order_by(desc(column)).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_last_login(self, user_id: int):
        user = await self.get_user(user_id)
        if user:
            user.last_login = datetime.now().date().isoformat()
            await self.session.commit()

    async def set_admin_status(self, user_id: int, is_admin: bool):
        user = await self.get_user(user_id)
        if user:
            user.is_admin = is_admin
            await self.session.commit()
        elif is_admin:
            # Create dummy user if admin needs to be set before registration
            user = User(id=user_id, is_admin=True)
            self.session.add(user)
            await self.session.commit()
