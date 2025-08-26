import json
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.dialog_sessions: Dict[str, List[int]] = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await self.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "message": "Connected to AI Chat Arena! 🎭"
        }, websocket)

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove from dialog sessions
        for session_id, clients in self.dialog_sessions.items():
            if client_id in clients:
                clients.remove(client_id)
                if not clients:
                    del self.dialog_sessions[session_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))

    async def send_to_session(self, session_id: str, message: dict):
        if session_id in self.dialog_sessions:
            for client_id in self.dialog_sessions[session_id]:
                if client_id in self.active_connections:
                    await self.send_personal_message(message, self.active_connections[client_id])

    async def join_dialog_session(self, session_id: str, client_id: int):
        if session_id not in self.dialog_sessions:
            self.dialog_sessions[session_id] = []
        self.dialog_sessions[session_id].append(client_id)
        
        # Notify session members
        await self.send_to_session(session_id, {
            "type": "user_joined",
            "client_id": client_id,
            "session_id": session_id,
            "message": f"User {client_id} joined the session"
        })

    async def leave_dialog_session(self, session_id: str, client_id: int):
        if session_id in self.dialog_sessions:
            if client_id in self.dialog_sessions[session_id]:
                self.dialog_sessions[session_id].remove(client_id)
                
                # Notify session members
                await self.send_to_session(session_id, {
                    "type": "user_left",
                    "client_id": client_id,
                    "session_id": session_id,
                    "message": f"User {client_id} left the session"
                })
                
                # Clean up empty sessions
                if not self.dialog_sessions[session_id]:
                    del self.dialog_sessions[session_id]

    async def send_drama_update(self, session_id: str, drama_level: float, message: str):
        """Send drama level updates for Reality Show Mode"""
        await self.send_to_session(session_id, {
            "type": "drama_update",
            "drama_level": drama_level,
            "message": message,
            "timestamp": str(datetime.now())
        })

    async def send_agent_emotion(self, agent_name: str, emotion: str, emoji: str):
        """Send agent emotion updates"""
        emotion_message = {
            "type": "agent_emotion",
            "agent_name": agent_name,
            "emotion": emotion,
            "emoji": emoji,
            "timestamp": str(datetime.now())
        }
        await self.broadcast(emotion_message)

    async def send_typing_indicator(self, agent_name: str, is_typing: bool):
        """Send typing indicators"""
        typing_message = {
            "type": "typing_indicator",
            "agent_name": agent_name,
            "is_typing": is_typing,
            "timestamp": str(datetime.now())
        }
        await self.broadcast(typing_message)

    def get_active_connections_count(self) -> int:
        return len(self.active_connections)

    def get_session_participants(self, session_id: str) -> List[int]:
        return self.dialog_sessions.get(session_id, [])

# Global instance
manager = ConnectionManager()