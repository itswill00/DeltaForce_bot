from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # Telegram User ID
    ign = Column(String(50), nullable=True)
    role = Column(String(20), nullable=True)
    first_name = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True)
    
    # Stats
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    rep_points = Column(Integer, default=0)
    mabar_score = Column(Integer, default=0)
    trivia_score = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    
    # Meta
    last_login = Column(String(20), nullable=True)
    is_admin = Column(Boolean, default=False)
    owned_items = Column(JSON, default=list) # List of item IDs
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, ign='{self.ign}', level={self.level})>"

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)  # Telegram Chat ID
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Settings (serialized to JSON for flexibility while keeping ACID)
    settings = Column(JSON, default={
        "auto_intel": False,
        "trivia_enabled": True,
        "auto_cleanup": True,
        "last_intel_post": ""
    })
    
    # For local analytics
    member_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<Group(id={self.id}, title='{self.title}')>"

class LFGSession(Base):
    __tablename__ = "lfg_sessions"

    id = Column(String(20), primary_key=True) # Short UUID
    host_id = Column(Integer, ForeignKey("users.id"))
    host_name = Column(String(100))
    lfg_type = Column(String(20)) # 'hazard' or 'havoc'
    max_players = Column(Integer)
    status = Column(String(20), default="open") # 'open', 'closed'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Players stored as JSON for simplicity in this specific many-to-many 
    # but could be a separate table for true enterprise normalization.
    # Given the bot's scale, JSON here is a mature compromise.
    players = Column(JSON, default=list) 

    def __repr__(self):
        return f"<LFGSession(id='{self.id}', host='{self.host_name}', status='{self.status}')>"
