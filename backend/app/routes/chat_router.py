from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime
import asyncio
import time
from sqlalchemy import select, func

from app.database import get_db, AsyncSession
from app.database import ChatHistory, AgentStats
from services.ollama_service import OllamaService
from services.agent_service import SplitDialogAgent, WahajacySieAgent

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    agent_type: str = "normal"
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    timestamp: str
    response_time: float

class SplitDialogRequest(BaseModel):
    topic: str
    max_turns: int = 5

class DoubtAgentRequest(BaseModel):
    query: str
    doubt_level: float = 0.5  # 0-1

# Initialize services
ollama_service = OllamaService()

@router.post("/normal", response_model=ChatResponse)
async def normal_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Normal chat with selected agent"""
    try:
        start_time = time.time()
        
        # Generate response
        response = await ollama_service.chat(request.query, request.agent_type)
        response_time = time.time() - start_time
        
        # Save to database
        from app.database import ChatHistory
        chat_record = ChatHistory(
            query=request.query,
            response=response,
            agent_type=request.agent_type,
            session_id=request.session_id,
            response_time=response_time
        )
        db.add(chat_record)
        await db.commit()
        
        return ChatResponse(
            response=response,
            agent_type=request.agent_type,
            timestamp=datetime.now().isoformat(),
            response_time=response_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/split-dialog")
async def split_dialog(
    request: SplitDialogRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate dialog between two agents"""
    try:
        agent = SplitDialogAgent()
        dialog = await agent.generate_dialog(request.topic, request.max_turns)
        
        # Save dialog session
        from app.database import DialogSession
        session_id = f"split_{int(time.time())}"
        dialog_session = DialogSession(
            session_id=session_id,
            agent1_name="Adam",
            agent2_name="Beata",
            topic=request.topic,
            messages=str(dialog)
        )
        db.add(dialog_session)
        await db.commit()
        
        return {
            "session_id": session_id,
            "dialog": dialog,
            "agents": ["Adam", "Beata"],
            "topic": request.topic
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doubt-agent")
async def doubt_agent(
    request: DoubtAgentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Chat with doubting agent"""
    try:
        start_time = time.time()
        
        agent = WahajacySieAgent()
        response = await agent.generate_response_with_doubt(request.query, request.doubt_level)
        response_time = time.time() - start_time
        
        # Save to database
        from app.database import ChatHistory
        chat_record = ChatHistory(
            query=request.query,
            response=response,
            agent_type="doubt",
            session_id=None,
            response_time=response_time
        )
        db.add(chat_record)
        await db.commit()
        
        return {
            "response": response,
            "agent_type": "doubt",
            "timestamp": datetime.now().isoformat(),
            "response_time": response_time,
            "doubt_level": request.doubt_level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def get_available_agents():
    """Get list of available agents"""
    return {
        "agents": [
            {
                "name": "normal",
                "display_name": "Normal AI",
                "description": "Standardowy asystent AI",
                "avatar": "🤖"
            },
            {
                "name": "adam",
                "display_name": "Adam",
                "description": "Optymistyczny agent (niebieska głowa)",
                "avatar": "🧠"
            },
            {
                "name": "beata",
                "display_name": "Beata",
                "description": "Sceptyczny agent (czerwona głowa z lupą)",
                "avatar": "🔍"
            },
            {
                "name": "doubt",
                "display_name": "Wątpiący",
                "description": "Niezdecydowany agent (żółty ze znakami zapytania)",
                "avatar": "❓"
            }
        ]
    }

@router.get("/stats")
async def get_chat_stats(db: AsyncSession = Depends(get_db)):
    """Get chat statistics"""
    try:
        # Total messages
        total_messages_result = await db.execute(select(func.count(ChatHistory.id)))
        total_messages = total_messages_result.scalar()
        
        # Messages by agent type
        agent_stats_result = await db.execute(
            select(ChatHistory.agent_type, func.count(ChatHistory.id))
            .group_by(ChatHistory.agent_type)
        )
        agent_stats = dict(agent_stats_result.fetchall())
        
        # Average response time
        avg_response_time_result = await db.execute(select(func.avg(ChatHistory.response_time)))
        avg_response_time = avg_response_time_result.scalar() or 0
        
        return {
            "total_messages": total_messages,
            "agent_stats": agent_stats,
            "average_response_time": avg_response_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))