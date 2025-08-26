import asyncio
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime
import sqlite3

# SQLite database URL
DATABASE_URL = "sqlite:///./ai_chat_arena.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    agent_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String(100), nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    response_time = Column(Float, nullable=True)  # in seconds
    
class AgentStats(Base):
    __tablename__ = "agent_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(50), nullable=False)
    total_messages = Column(Integer, default=0)
    total_doubts = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    user_satisfaction = Column(Float, default=0.0)  # 0-1
    last_used = Column(DateTime, default=datetime.utcnow)
    
class DialogSession(Base):
    __tablename__ = "dialog_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, unique=True)
    agent1_name = Column(String(50), nullable=False)
    agent2_name = Column(String(50), nullable=False)
    topic = Column(Text, nullable=True)
    messages = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    drama_level = Column(Float, default=0.0)  # 0-1 drama meter

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create some initial agent stats
    async with AsyncSessionLocal() as session:
        # Check if stats exist
        result = await session.execute("SELECT COUNT(*) FROM agent_stats")
        count = result.scalar()
        
        if count == 0:
            # Create initial agent stats
            agents = [
                {"agent_name": "Adam", "total_messages": 0, "total_doubts": 0, "avg_response_time": 0.0, "user_satisfaction": 0.0},
                {"agent_name": "Beata", "total_messages": 0, "total_doubts": 0, "avg_response_time": 0.0, "user_satisfaction": 0.0},
                {"agent_name": "Wątpiący", "total_messages": 0, "total_doubts": 0, "avg_response_time": 0.0, "user_satisfaction": 0.0},
            ]
            
            for agent_data in agents:
                agent = AgentStats(**agent_data)
                session.add(agent)
            
            await session.commit()
            print("📊 Initial agent stats created")

async def get_db() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# For synchronous operations (when needed)
def get_sync_db():
    """Get synchronous database session for compatibility"""
    engine_sync = create_engine(DATABASE_URL.replace("+aiosqlite", ""))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)
    return SessionLocal()