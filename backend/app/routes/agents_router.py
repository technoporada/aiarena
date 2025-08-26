from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
import asyncio
import time
import random

from app.database import get_db, AsyncSession
from services.agent_service import SplitDialogAgent, WahajacySieAgent
from services.ollama_service import OllamaService

router = APIRouter()

class AgentConfig(BaseModel):
    name: str
    personality: str
    voice_settings: Dict[str, Any] = None
    avatar_settings: Dict[str, Any] = None

class RealityShowRequest(BaseModel):
    topic: str
    duration: int = 60  # seconds
    drama_level: float = 0.5

class RoastModeRequest(BaseModel):
    target: str  # user or agent name
    intensity: float = 0.7  # 0-1

class AgentResponse(BaseModel):
    agent_name: str
    response: str
    emotion: str
    emoji: str
    confidence: float
    timestamp: str

@router.get("/list")
async def get_agents_list():
    """Get list of all available agents"""
    return {
        "agents": [
            {
                "id": "adam",
                "name": "Adam",
                "personality": "Optymistyczny i pełen entuzjazmu",
                "avatar": "🧠",
                "color": "blue",
                "voice": "cheerful",
                "strengths": ["kreatywność", "pozytywne myślenie", "motywacja"],
                "weaknesses": ["czasem naiwny", "zbyt optymistyczny"]
            },
            {
                "id": "beata",
                "name": "Beata",
                "personality": "Sceptyczna i analityczna",
                "avatar": "🔍",
                "color": "red",
                "voice": "serious",
                "strengths": ["krytyczne myślenie", "dokładność", "logika"],
                "weaknesses": ["zbyt krytyczna", "brak empatii"]
            },
            {
                "id": "wapiacy",
                "name": "Wątpiący",
                "personality": "Niezdecydowany i pełen wątpliwości",
                "avatar": "❓",
                "color": "yellow",
                "voice": "uncertain",
                "strengths": ["ostrożność", "analiza ryzyka", "uważność"],
                "weaknesses": ["paraliż decyzyjny", "zbyt wiele pytań"]
            }
        ]
    }

@router.get("/{agent_id}/stats")
async def get_agent_stats(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific agent statistics"""
    try:
        from app.database import AgentStats
        
        # Get agent stats from database
        result = await db.execute(
            f"SELECT * FROM agent_stats WHERE agent_name = '{agent_id}'"
        )
        stats = result.fetchone()
        
        if not stats:
            # Create default stats
            stats = {
                "agent_name": agent_id,
                "total_messages": 0,
                "total_doubts": 0,
                "avg_response_time": 0.0,
                "user_satisfaction": 0.0,
                "last_used": datetime.now().isoformat()
            }
        else:
            stats = dict(stats)
            stats["last_used"] = stats["last_used"].isoformat()
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reality-show")
async def start_reality_show(
    request: RealityShowRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start reality show mode with agents arguing"""
    try:
        split_agent = SplitDialogAgent()
        
        # Generate dramatic dialog
        dialog = await split_agent.generate_dramatic_dialog(
            request.topic, 
            duration=request.duration,
            drama_level=request.drama_level
        )
        
        # Calculate drama metrics
        drama_score = calculate_drama_score(dialog)
        
        # Save session
        from app.database import DialogSession
        session_id = f"reality_{int(time.time())}"
        dialog_session = DialogSession(
            session_id=session_id,
            agent1_name="Adam",
            agent2_name="Beata",
            topic=request.topic,
            messages=str(dialog),
            drama_level=drama_score
        )
        db.add(dialog_session)
        await db.commit()
        
        return {
            "session_id": session_id,
            "dialog": dialog,
            "drama_score": drama_score,
            "topic": request.topic,
            "duration": request.duration,
            "participants": ["Adam", "Beata"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/roast-mode")
async def roast_mode(
    request: RoastModeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate funny roasts about user or agents"""
    try:
        ollama_service = OllamaService()
        
        # Create roast prompt based on target
        if request.target == "user":
            prompt = f"""
            You are a comedian AI. Write a funny, light-hearted roast about the user.
            Make it playful and not actually mean. Include some self-deprecating humor too.
            Intensity level: {request.intensity}
            Keep it short and witty.
            """
        else:
            prompt = f"""
            You are a comedian AI. Write a funny roast about {request.target} agent.
            Make it playful and focus on their personality quirks.
            Intensity level: {request.intensity}
            Keep it short and witty.
            """
        
        roast = await ollama_service.generate_creative_content(prompt)
        
        return {
            "target": request.target,
            "roast": roast,
            "intensity": request.intensity,
            "timestamp": datetime.now().isoformat(),
            "funny_score": random.uniform(0.6, 0.95)  # Simulated funny score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mini-game/guess-agent")
async def guess_agent_game(
    responses: List[str],
    db: AsyncSession = Depends(get_db)
):
    """Mini-game: guess which agent gave each response"""
    try:
        # For now, shuffle and return as a game
        random.shuffle(responses)
        
        return {
            "game_type": "guess_agent",
            "responses": responses,
            "possible_agents": ["Adam", "Beata", "Wątpiący"],
            "instructions": "Zgadnij, który agent udzielił każdej odpowiedzi!",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config")
async def update_agent_config(
    agent_id: str,
    config: AgentConfig,
    db: AsyncSession = Depends(get_db)
):
    """Update agent configuration"""
    try:
        # In a real implementation, this would save to database
        # For now, just return success
        return {
            "agent_id": agent_id,
            "config": config.dict(),
            "message": "Konfiguracja zaktualizowana pomyślnie",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_drama_score(dialog: List[Dict]) -> float:
    """Calculate drama score from dialog"""
    drama_keywords = ["!", "?", "absurd", "niewiarygodne", "szaleństwo", "skandal"]
    score = 0.0
    
    for message in dialog:
        text = message.get("text", "").lower()
        for keyword in drama_keywords:
            score += text.count(keyword) * 0.1
        
        # Add points for exclamation marks and questions
        score += text.count("!") * 0.05
        score += text.count("?") * 0.03
    
    return min(score, 1.0)  # Cap at 1.0