from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
from sqlalchemy import select, func

from app.database import get_db, AsyncSession
from app.database import ChatHistory, DialogSession

router = APIRouter()

class HistoryResponse(BaseModel):
    id: int
    query: str
    response: str
    agent_type: str
    timestamp: str
    session_id: Optional[str]
    user_rating: Optional[int]
    response_time: Optional[float]

class DialogSessionResponse(BaseModel):
    session_id: str
    agent1_name: str
    agent2_name: str
    topic: Optional[str]
    messages: Optional[str]
    created_at: str
    is_active: bool
    drama_level: float

class ExportRequest(BaseModel):
    format: str = "json"  # json, txt, csv
    session_id: Optional[str] = None
    agent_type: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None

@router.get("/chat", response_model=List[HistoryResponse])
async def get_chat_history(
    limit: int = Query(50, le=1000),
    offset: int = Query(0, ge=0),
    agent_type: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get chat history with filters"""
    try:
        # Build query
        query = select(ChatHistory)
        
        if agent_type:
            query = query.where(ChatHistory.agent_type == agent_type)
        
        if session_id:
            query = query.where(ChatHistory.session_id == session_id)
        
        if date_from:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.where(ChatHistory.timestamp >= from_date)
        
        if date_to:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.where(ChatHistory.timestamp <= to_date)
        
        # Apply pagination
        query = query.order_by(ChatHistory.timestamp.desc()).offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        history = result.scalars().all()
        
        # Convert to response format
        response = []
        for item in history:
            response.append(HistoryResponse(
                id=item.id,
                query=item.query,
                response=item.response,
                agent_type=item.agent_type,
                timestamp=item.timestamp.isoformat(),
                session_id=item.session_id,
                user_rating=item.user_rating,
                response_time=item.response_time
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[DialogSessionResponse])
async def get_dialog_sessions(
    limit: int = Query(50, le=1000),
    offset: int = Query(0, ge=0),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get dialog sessions"""
    try:
        query = select(DialogSession)
        
        if is_active is not None:
            query = query.where(DialogSession.is_active == is_active)
        
        query = query.order_by(DialogSession.created_at.desc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        response = []
        for session in sessions:
            response.append(DialogSessionResponse(
                session_id=session.session_id,
                agent1_name=session.agent1_name,
                agent2_name=session.agent2_name,
                topic=session.topic,
                messages=session.messages,
                created_at=session.created_at.isoformat(),
                is_active=session.is_active,
                drama_level=session.drama_level
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_dialog_session_details(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific dialog session details"""
    try:
        result = await db.execute(
            select(DialogSession).where(DialogSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Parse messages if they exist
        messages = []
        if session.messages:
            try:
                messages = json.loads(session.messages)
            except:
                messages = []
        
        return {
            "session_id": session.session_id,
            "agent1_name": session.agent1_name,
            "agent2_name": session.agent2_name,
            "topic": session.topic,
            "messages": messages,
            "created_at": session.created_at.isoformat(),
            "is_active": session.is_active,
            "drama_level": session.drama_level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview")
async def get_history_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get history statistics overview"""
    try:
        # Calculate date range
        from_date = datetime.now() - timedelta(days=days)
        
        # Total messages in period
        total_messages_result = await db.execute(
            select(func.count(ChatHistory.id)).where(ChatHistory.timestamp >= from_date)
        )
        total_messages = total_messages_result.scalar()
        
        # Messages by agent type
        agent_stats_result = await db.execute(
            select(ChatHistory.agent_type, func.count(ChatHistory.id))
            .where(ChatHistory.timestamp >= from_date)
            .group_by(ChatHistory.agent_type)
        )
        agent_stats = dict(agent_stats_result.fetchall())
        
        # Average response time
        avg_response_time_result = await db.execute(
            select(func.avg(ChatHistory.response_time)).where(ChatHistory.timestamp >= from_date)
        )
        avg_response_time = avg_response_time_result.scalar() or 0
        
        # Total sessions
        total_sessions_result = await db.execute(
            select(func.count(DialogSession.id)).where(DialogSession.created_at >= from_date)
        )
        total_sessions = total_sessions_result.scalar()
        
        # Average drama level
        avg_drama_result = await db.execute(
            select(func.avg(DialogSession.drama_level)).where(DialogSession.created_at >= from_date)
        )
        avg_drama = avg_drama_result.scalar() or 0
        
        return {
            "period_days": days,
            "total_messages": total_messages,
            "agent_stats": agent_stats,
            "average_response_time": avg_response_time,
            "total_sessions": total_sessions,
            "average_drama_level": avg_drama,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_history(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Export chat history in various formats"""
    try:
        # Build query based on filters
        query = select(ChatHistory)
        
        if request.session_id:
            query = query.where(ChatHistory.session_id == request.session_id)
        
        if request.agent_type:
            query = query.where(ChatHistory.agent_type == request.agent_type)
        
        if request.date_from:
            from_date = datetime.fromisoformat(request.date_from.replace('Z', '+00:00'))
            query = query.where(ChatHistory.timestamp >= from_date)
        
        if request.date_to:
            to_date = datetime.fromisoformat(request.date_to.replace('Z', '+00:00'))
            query = query.where(ChatHistory.timestamp <= to_date)
        
        # Get data
        result = await db.execute(query)
        history = result.scalars().all()
        
        # Convert to list of dicts
        data = []
        for item in history:
            data.append({
                "id": item.id,
                "query": item.query,
                "response": item.response,
                "agent_type": item.agent_type,
                "timestamp": item.timestamp.isoformat(),
                "session_id": item.session_id,
                "user_rating": item.user_rating,
                "response_time": item.response_time
            })
        
        # Format based on request
        if request.format == "json":
            return {
                "format": "json",
                "data": data,
                "exported_at": datetime.now().isoformat(),
                "total_records": len(data)
            }
        
        elif request.format == "txt":
            # Create text format
            text_content = f"AI Chat Arena - Export History\n"
            text_content += f"Exported at: {datetime.now().isoformat()}\n"
            text_content += f"Total records: {len(data)}\n"
            text_content += "=" * 50 + "\n\n"
            
            for item in data:
                text_content += f"Time: {item['timestamp']}\n"
                text_content += f"Agent: {item['agent_type']}\n"
                text_content += f"Query: {item['query']}\n"
                text_content += f"Response: {item['response']}\n"
                text_content += "-" * 30 + "\n\n"
            
            return {
                "format": "txt",
                "content": text_content,
                "exported_at": datetime.now().isoformat(),
                "total_records": len(data)
            }
        
        elif request.format == "csv":
            # Create CSV format
            csv_content = "id,timestamp,agent_type,query,response,session_id,user_rating,response_time\n"
            
            for item in data:
                csv_content += f"{item['id']},{item['timestamp']},{item['agent_type']},\"{item['query']}\",\"{item['response']}\",{item['session_id']},{item['user_rating']},{item['response_time']}\n"
            
            return {
                "format": "csv",
                "content": csv_content,
                "exported_at": datetime.now().isoformat(),
                "total_records": len(data)
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/{message_id}")
async def delete_chat_message(
    message_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific chat message"""
    try:
        result = await db.execute(
            select(ChatHistory).where(ChatHistory.id == message_id)
        )
        message = result.scalar_one_or_none()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        await db.delete(message)
        await db.commit()
        
        return {"message": "Message deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_dialog_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a dialog session"""
    try:
        result = await db.execute(
            select(DialogSession).where(DialogSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await db.delete(session)
        await db.commit()
        
        return {"message": "Session deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))