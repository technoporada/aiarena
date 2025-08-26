from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import io
import base64
import asyncio
import tempfile
import os

from services.tts_service import TTSService

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "default"
    speed: float = 1.0
    pitch: float = 1.0
    emotion: str = "neutral"

class VoiceConfig(BaseModel):
    voice_id: str
    name: str
    language: str
    gender: str
    description: str
    preview_text: str

class TTSService:
    def __init__(self):
        self.voices = {
            "adam": {
                "name": "Adam (Optymista)",
                "language": "pl-PL",
                "gender": "male",
                "engine": "pyttsx3",
                "properties": {
                    "rate": 150,
                    "volume": 0.9,
                    "voice_id": None
                }
            },
            "beata": {
                "name": "Beata (Sceptyczna)",
                "language": "pl-PL", 
                "gender": "female",
                "engine": "pyttsx3",
                "properties": {
                    "rate": 130,
                    "volume": 0.8,
                    "voice_id": None
                }
            },
            "wapiacy": {
                "name": "Wątpiący",
                "language": "pl-PL",
                "gender": "male",
                "engine": "pyttsx3", 
                "properties": {
                    "rate": 100,
                    "volume": 0.7,
                    "voice_id": None
                }
            },
            "gtts_adam": {
                "name": "Adam (GTTS)",
                "language": "pl",
                "gender": "male",
                "engine": "gtts",
                "properties": {
                    "speed": 1.2,
                    "lang": "pl"
                }
            },
            "gtts_beata": {
                "name": "Beata (GTTS)",
                "language": "pl",
                "gender": "female", 
                "engine": "gtts",
                "properties": {
                    "speed": 1.0,
                    "lang": "pl"
                }
            }
        }
        
        self.tts_service = TTSService()

@router.get("/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    voices = []
    for voice_id, config in tts_service.voices.items():
        voices.append(VoiceConfig(
            voice_id=voice_id,
            name=config["name"],
            language=config["language"],
            gender=config["gender"],
            description=config.get("description", f"Głos dla {config['name']}"),
            preview_text="Cześć! Jestem AI gotowy do rozmowy!"
        ))
    
    return {"voices": voices}

@router.post("/generate")
async def generate_speech(request: TTSRequest):
    """Generate speech from text"""
    try:
        # Get voice configuration
        if request.voice_id not in tts_service.voices:
            raise HTTPException(status_code=400, detail="Voice not found")
        
        voice_config = tts_service.voices[request.voice_id]
        
        # Generate audio
        audio_data = await tts_service.tts_service.generate_speech(
            text=request.text,
            voice_config=voice_config,
            speed=request.speed,
            pitch=request.pitch,
            emotion=request.emotion
        )
        
        # Convert to base64 for web transmission
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return {
            "audio_data": audio_base64,
            "format": "audio/mp3",
            "voice_id": request.voice_id,
            "text": request.text,
            "duration_estimate": len(request.text) * 0.1,  # Rough estimate
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-file")
async def generate_speech_file(request: TTSRequest):
    """Generate speech file and return download URL"""
    try:
        if request.voice_id not in tts_service.voices:
            raise HTTPException(status_code=400, detail="Voice not found")
        
        voice_config = tts_service.voices[request.voice_id]
        
        # Generate temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            audio_data = await tts_service.tts_service.generate_speech(
                text=request.text,
                voice_config=voice_config,
                speed=request.speed,
                pitch=request.pitch,
                emotion=request.emotion
            )
            
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name
        
        # In a real app, you'd upload to cloud storage and return URL
        # For now, return file info
        return {
            "file_path": tmp_file_path,
            "filename": f"speech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "voice_id": request.voice_id,
            "text": request.text,
            "file_size": len(audio_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-generate")
async def batch_generate_speech(requests: list[TTSRequest]):
    """Generate multiple speech files"""
    try:
        results = []
        
        for req in requests:
            if req.voice_id not in tts_service.voices:
                results.append({
                    "error": f"Voice {req.voice_id} not found",
                    "request": req.dict()
                })
                continue
            
            voice_config = tts_service.voices[req.voice_id]
            
            try:
                audio_data = await tts_service.tts_service.generate_speech(
                    text=req.text,
                    voice_config=voice_config,
                    speed=req.speed,
                    pitch=req.pitch,
                    emotion=req.emotion
                )
                
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                results.append({
                    "success": True,
                    "audio_data": audio_base64,
                    "voice_id": req.voice_id,
                    "text": req.text,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "request": req.dict()
                })
        
        return {
            "results": results,
            "total_requests": len(requests),
            "successful": len([r for r in results if r.get("success", False)]),
            "failed": len([r for r in results if not r.get("success", False)]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{voice_id}")
async def preview_voice(voice_id: str):
    """Generate preview audio for a voice"""
    try:
        if voice_id not in tts_service.voices:
            raise HTTPException(status_code=400, detail="Voice not found")
        
        voice_config = tts_service.voices[voice_id]
        preview_text = "Cześć! Jestem gotowy do rozmowy. To jest moj głos demonstracyjny!"
        
        audio_data = await tts_service.tts_service.generate_speech(
            text=preview_text,
            voice_config=voice_config,
            speed=1.0,
            pitch=1.0,
            emotion="neutral"
        )
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return {
            "audio_data": audio_base64,
            "format": "audio/mp3",
            "voice_id": voice_id,
            "text": preview_text,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emotion-mapping")
async def get_emotion_mapping():
    """Get emotion-to-voice-parameter mapping"""
    return {
        "emotions": {
            "happy": {
                "speed_multiplier": 1.2,
                "pitch_multiplier": 1.1,
                "volume_multiplier": 1.0,
                "description": "Szybkie, wysokie tonacje, pełne energii"
            },
            "sad": {
                "speed_multiplier": 0.8,
                "pitch_multiplier": 0.9,
                "volume_multiplier": 0.7,
                "description": "Wolne, niskie tonacje, ciche"
            },
            "angry": {
                "speed_multiplier": 1.3,
                "pitch_multiplier": 1.2,
                "volume_multiplier": 1.2,
                "description": "Szybkie, wysokie, głośne"
            },
            "surprised": {
                "speed_multiplier": 1.4,
                "pitch_multiplier": 1.3,
                "volume_multiplier": 1.1,
                "description": "Bardzo szybkie, bardzo wysokie tonacje"
            },
            "neutral": {
                "speed_multiplier": 1.0,
                "pitch_multiplier": 1.0,
                "volume_multiplier": 1.0,
                "description": "Normalne parametry"
            },
            "doubtful": {
                "speed_multiplier": 0.9,
                "pitch_multiplier": 0.95,
                "volume_multiplier": 0.8,
                "description": "Nieco wolniejsze, niższe, cichsze"
            },
            "excited": {
                "speed_multiplier": 1.5,
                "pitch_multiplier": 1.4,
                "volume_multiplier": 1.3,
                "description": "Bardzo szybkie, wysokie, głośne, pełne entuzjazmu"
            }
        }
    }

@router.delete("/cache")
async def clear_tts_cache():
    """Clear TTS cache (if implemented)"""
    try:
        # This would clear any cached audio files
        cache_cleared = await tts_service.tts_service.clear_cache()
        
        return {
            "message": "TTS cache cleared",
            "cache_cleared": cache_cleared,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize TTS service
tts_service = TTSService()