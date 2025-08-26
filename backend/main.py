from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import json
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from app.routes import chat_router, agents_router, history_router, tts_router, gladiator_router, karaoke_router, tsunami_router, ufo_conspiracy_router
from app.database import init_db
from app.websocket import manager
from services.ollama_service import OllamaService
from services.agent_service import SplitDialogAgent, WahajacySieAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting AI Chat Backend...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down...")

app = FastAPI(
    title="AI Chat Arena",
    description="Rozrywkowa platforma AI z animowanymi agentami",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
ollama_service = OllamaService()

# Include routers
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(agents_router, prefix="/api/agents", tags=["Agents"])
app.include_router(history_router, prefix="/api/history", tags=["History"])
app.include_router(tts_router, prefix="/api/tts", tags=["TTS"])
app.include_router(gladiator_router, prefix="/api/gladiator", tags=["Gladiator"])
app.include_router(karaoke_router, prefix="/api/karaoke", tags=["Karaoke"])
app.include_router(tsunami_router, prefix="/api/tsunami", tags=["Tsunami"])
app.include_router(ufo_conspiracy_router, prefix="/api/ufo-conspiracy", tags=["UFO Conspiracy"])

@app.get("/")
async def root():
    return {"message": "🎭 AI Chat Arena Backend", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "chat":
                response = await ollama_service.chat(message["query"], message["agent_type"])
                await manager.send_personal_message({
                    "type": "chat_response",
                    "response": response,
                    "agent_type": message["agent_type"]
                }, websocket)
                
            elif message["type"] == "split_dialog":
                agent = SplitDialogAgent()
                dialog = await agent.generate_dialog(message["topic"])
                await manager.send_personal_message({
                    "type": "split_dialog",
                    "dialog": dialog
                }, websocket)
                
            elif message["type"] == "doubt_agent":
                agent = WahajacySieAgent()
                response = await agent.generate_response_with_doubt(message["query"])
                await manager.send_personal_message({
                    "type": "doubt_response",
                    "response": response
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left the chat")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )