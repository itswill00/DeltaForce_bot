from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from database.models import Base
import os

# Use SQLite for portability, can easily be changed to PostgreSQL
DATABASE_URL = "sqlite+aiosqlite:///deltaforce.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
