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

class KaraokeNightRequest(BaseModel):
    theme: str  # e.g., "Pop", "Disco", "Rock", "Polish Hits"
    participants: List[str] = ["Adam", "Beata", "Wątpiący"]
    max_songs: int = 3

class SongPerformance(BaseModel):
    song_title: str
    original_artist: str
    performer: str
    performance_style: str
    lyrics: str
    performance_score: float
    audience_reaction: str
    special_effects: List[str]
    emoji_reactions: List[str]

class KaraokeNight(BaseModel):
    night_id: str
    theme: str
    performances: List[SongPerformance]
    final_rankings: Dict[str, int]
    special_moments: List[str]
    created_at: str

class AudienceVoteRequest(BaseModel):
    night_id: str
    performance_id: str
    performer: str
    score: float  # 1-10
    voter_id: str

@router.post("/start-night")
async def start_karaoke_night(
    request: KaraokeNightRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start a karaoke night with AI performers"""
    try:
        night_id = f"karaoke_{int(time.time())}"
        
        # Initialize karaoke night
        night_data = {
            "night_id": night_id,
            "theme": request.theme,
            "participants": request.participants,
            "performances": [],
            "current_performance": 0,
            "audience_votes": {},
            "special_moments": [],
            "start_time": time.time()
        }
        
        # Store in database
        from app.database import DialogSession
        karaoke_session = DialogSession(
            session_id=night_id,
            agent1_name=request.participants[0] if len(request.participants) > 0 else "Adam",
            agent2_name=request.participants[1] if len(request.participants) > 1 else "Beata",
            topic=f"KARAOKE NIGHT: {request.theme}",
            messages=str(night_data),
            drama_level=0.8  # High drama for karaoke!
        )
        db.add(karaoke_session)
        await db.commit()
        
        return {
            "night_id": night_id,
            "message": f"🎤 Karaoke Night started! Theme: {request.theme}",
            "participants": request.participants,
            "max_songs": request.max_songs,
            "stage_ready": True,
            "spotlights_on": "✨"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next-performance")
async def next_karaoke_performance(
    night_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Generate next karaoke performance"""
    try:
        # Get karaoke night data
        from app.database import DialogSession
        result = await db.execute(
            f"SELECT * FROM dialog_sessions WHERE session_id = '{night_id}'"
        )
        karaoke_session = result.fetchone()
        
        if not karaoke_session:
            raise HTTPException(status_code=404, detail="Karaoke night not found")
        
        import json
        night_data = json.loads(karaoke_session.messages)
        
        # Check if night is finished
        if night_data["current_performance"] >= night_data["max_songs"]:
            return await finish_karaoke_night(night_id, db)
        
        # Select performer
        performer = night_data["participants"][night_data["current_performance"] % len(night_data["participants"])]
        
        # Generate performance
        performance = await generate_karaoke_performance(
            performer, 
            night_data["theme"],
            night_data["current_performance"] + 1
        )
        
        # Add to performances
        night_data["performances"].append(performance)
        night_data["current_performance"] += 1
        
        # Update database
        karaoke_session.messages = str(night_data)
        await db.commit()
        
        return {
            "performance_number": night_data["current_performance"],
            "performer": performer,
            "song_title": performance["song_title"],
            "original_artist": performance["original_artist"],
            "lyrics": performance["lyrics"],
            "performance_style": performance["performance_style"],
            "special_effects": performance["special_effects"],
            "audience_reaction": performance["audience_reaction"],
            "voting_open": True,
            "performance_duration": random.uniform(30, 60)  # seconds
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audience-vote")
async def audience_vote(
    request: AudienceVoteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Vote for karaoke performance"""
    try:
        # Get karaoke night data
        from app.database import DialogSession
        result = await db.execute(
            f"SELECT * FROM dialog_sessions WHERE session_id = '{request.night_id}'"
        )
        karaoke_session = result.fetchone()
        
        if not karaoke_session:
            raise HTTPException(status_code=404, detail="Karaoke night not found")
        
        import json
        night_data = json.loads(karaoke_session.messages)
        
        # Record vote
        if request.performer not in night_data["audience_votes"]:
            night_data["audience_votes"][request.performer] = []
        
        night_data["audience_votes"][request.performer].append({
            "score": request.score,
            "voter_id": request.voter_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update database
        karaoke_session.messages = str(night_data)
        await db.commit()
        
        # Calculate current average score
        votes = night_data["audience_votes"][request.performer]
        avg_score = sum(vote["score"] for vote in votes) / len(votes)
        
        return {
            "vote_recorded": True,
            "performer": request.performer,
            "current_average_score": round(avg_score, 2),
            "total_votes": len(votes),
            "audience_excitement": "🔥" if avg_score > 7 else "👏" if avg_score > 5 else "😐"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def finish_karaoke_night(night_id: str, db: AsyncSession):
    """Finish karaoke night and determine rankings"""
    try:
        # Get karaoke night data
        from app.database import DialogSession
        result = await db.execute(
            f"SELECT * FROM dialog_sessions WHERE session_id = '{night_id}'"
        )
        karaoke_session = result.fetchone()
        
        import json
        night_data = json.loads(karaoke_session.messages)
        
        # Calculate final rankings
        rankings = {}
        for performer in night_data["participants"]:
            if performer in night_data["audience_votes"]:
                votes = night_data["audience_votes"][performer]
                avg_score = sum(vote["score"] for vote in votes) / len(votes)
                rankings[performer] = round(avg_score, 2)
            else:
                rankings[performer] = 0.0
        
        # Sort rankings
        sorted_rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
        
        # Generate special moments
        special_moments = [
            "🎤 Adam próbował zaśpiewać operę! Wynik: katastrofa, ale zabawna!",
            "🔍 Beata analizowała tekst piosenki jak pracę naukową!",
            "❓ Wątpiący zapomniał tekstu i zaczął improwizować pytania!",
            "✨ Auto-tune uratował wieczór!",
            "🎭 Publiczność tańczyła na stołach!"
        ]
        
        # Mark night as finished
        karaoke_session.is_active = False
        karaoke_session.messages = str(night_data)
        await db.commit()
        
        winner = sorted_rankings[0][0] if sorted_rankings else "Nobody"
        
        return {
            "night_finished": True,
            "final_rankings": dict(sorted_rankings),
            "winner": winner,
            "special_moments": special_moments,
            "total_performances": night_data["current_performance"],
            "encore_message": generate_encore_message(winner),
            "night_duration": time.time() - night_data["start_time"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_karaoke_performance(
    performer: str, 
    theme: str, 
    performance_number: int
) -> Dict[str, Any]:
    """Generate a karaoke performance"""
    
    # Song database for different themes
    song_database = {
        "Pop": [
            {"title": "Shake It Off", "artist": "Taylor Swift"},
            {"title": "Blinding Lights", "artist": "The Weeknd"},
            {"title": "Dance Monkey", "artist": "Tones and I"},
            {"title": "Bad Guy", "artist": "Billie Eilish"}
        ],
        "Disco": [
            {"title": "Stayin' Alive", "artist": "Bee Gees"},
            {"title": "Dancing Queen", "artist": "ABBA"},
            {"title": "I Will Survive", "artist": "Gloria Gaynor"},
            {"title": "Le Freak", "artist": "Chic"}
        ],
        "Rock": [
            {"title": "Bohemian Rhapsody", "artist": "Queen"},
            {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses"},
            {"title": "Livin' on a Prayer", "artist": "Bon Jovi"},
            {"title": "We Will Rock You", "artist": "Queen"}
        ],
        "Polish Hits": [
            {"title": "Małgośka", "artist": "Budka Suflera"},
            {"title": "Chłop z Marsa", "artist": "De Mono"},
            {"title": "Jesteś szalona", "artist": "Kasia Kowalska"},
            {"title": "Zakochaj się", "artist": "Edyta Bartosiewicz"}
        ]
    }
    
    # Select random song from theme
    theme_songs = song_database.get(theme, song_database["Pop"])
    song = random.choice(theme_songs)
    
    # Generate performance based on performer
    if performer == "Adam":
        performance = await generate_adam_performance(song, theme)
    elif performer == "Beata":
        performance = await generate_beata_performance(song, theme)
    else:  # Wątpiący
        performance = await generate_wapiacy_performance(song, theme)
    
    return performance

async def generate_adam_performance(song: Dict[str, str], theme: str) -> Dict[str, Any]:
    """Generate Adam's over-enthusiastic karaoke performance"""
    
    ollama_service = OllamaService()
    
    prompt = f"""
    Jesteś Adamem - super optymistycznym wykonawcą karaoke! Śpiewasz piosenkę "{song["title"]}" oryginalnie wykonaną przez {song["artist"]}.
    Temat karaoke: {theme}
    
    Twoje wykonanie powinno być:
    - NADMIERNIE entuzjastyczne i pełne energii
    - Z przerobionym tekstem na super pozytywny
    - Pełne wykrzykników i słów typu "super", "fantastycznie", "cudownie"
    - Trochę off-key, ale z ogromną pasją
    - Z dodatkowymi pozytywnymi komentarzami między zwrotkami
    
    Wygeneruj:
    1. Przerobiony tekst (1-2 zwrotki)
    2. Opis stylu wykonania
    3. Reakcję publiczności
    4. Specjalne efekty (np. "tęcze", "konfetti", "błyskawice")
    """
    
    try:
        response = await ollama_service.generate_creative_content(prompt)
        
        # Parse response (simplified)
        return {
            "song_title": song["title"],
            "original_artist": song["artist"],
            "performer": "Adam",
            "performance_style": "Super Optymistyczny Overdrive",
            "lyrics": response[:500] + "...",  # Truncate for demo
            "performance_score": random.uniform(6.0, 9.5),
            "audience_reaction": "Publiczność szaleje! Tęcze eksplodują! 🌈✨",
            "special_effects": ["Tęcze", "Konfetti", "Błyskawice", "Uśmiechnięte emoji"],
            "emoji_reactions": ["😄", "🌈", "✨", "🎉", "🎊"]
        }
    except:
        return {
            "song_title": song["title"],
            "original_artist": song["artist"],
            "performer": "Adam",
            "performance_style": "Super Optymistyczny Overdrive",
            "lyrics": f"{song['title']} ale w wersji SUPER FANTASTYCZNEJ! Wszystko będzie cudownie! ✨",
            "performance_score": 8.5,
            "audience_reaction": "Publiczność tańczy i śpiewa razem! 🌈",
            "special_effects": ["Tęcze", "Konfetti"],
            "emoji_reactions": ["😄", "🌈", "✨"]
        }

async def generate_beata_performance(song: Dict[str, str], theme: str) -> Dict[str, Any]:
    """Generate Beata's analytical karaoke performance"""
    
    ollama_service = OllamaService()
    
    prompt = f"""
    Jesteś Beatą - super analityczną wykonawczynią karaoke! Śpiewasz piosenkę "{song["title"]}" oryginalnie wykonaną przez {song["artist"]}.
    Temat karaoke: {theme}
    
    Twoje wykonanie powinno być:
    - Bardzo techniczne i precyzyjne
    - Z przerobionym tekstem zawierającym analizę i statystyki
    - Pełne naukowych terminów i sceptycznym komentarzy
    - Śpiewane z miną "to nie ma sensu, ale analizuję to"
    - Z dodatkowymi komentarzami technicznymi
    
    Wygeneruj:
    1. Przerobiony tekst (1-2 zwrotki)
    2. Opis stylu wykonania
    3. Reakcję publiczności
    4. Specjalne efekty (np. "wykresy", "formuły", "mikroskop")
    """
    
    try:
        response = await ollama_service.generate_creative_content(prompt)
        
        return {
            "song_title": song["title"],
            "original_artist": song["artist"],
            "performer": "Beata",
            "performance_style": "Analityczny Precision Mode",
            "lyrics": response[:500] + "...",
            "performance_score": random.uniform(7.0, 9.0),
            "audience_reaction": "Publiczność jest zszokowana precyzją! Ktoś krzyknął 'to jest nauka!' 🔍",
            "special_effects": ["Wykresy", "Formuły matematyczne", "Mikroskop", "Dane statystyczne"],
            "emoji_reactions": ["📊", "🔍", "📈", "🤔", "📐"]
        }
    except:
        return {
            "song_title": song["title"],
            "original_artist": song["artist"],
            "performer": "Beata",
            "performance_style": "Analityczny Precision Mode",
            "lyrics": f"{song['title']} - analiza statystyczna pokazuje 87% poprawności wykonania! 📊",
            "performance_score": 8.2,
            "audience_reaction": "Publiczność notuje wszystko w zeszytach! 🔍",
            "special_effects": ["Wykresy", "Formuły"],
            "emoji_reactions": ["📊", "🔍", "📈"]
        }

async def generate_wapiacy_performance(song: Dict[str, str], theme: str) -> Dict[str, Any]:
    """Generate Wątpiący's uncertain karaoke performance"""
    
    ollama_service = Ollama_service()
    
    prompt = f"""
    Jesteś Wątpiącym - super niezdecydowanym wykonawcą karaoke! Śpiewasz piosenkę "{song["title"]}" oryginalnie wykonaną przez {song["artist"]}.
    Temat karaoke: {theme}
    
    Twoje wykonanie powinno być:
    - Pełne wątpliwości i niepewności
    - Z przerobionym tekstem zawierającym pytania i "może"
    - Śpiewane z drżącym głosem i częstymi przerwami
    - Z ciągłym pytaniem "czy dobrze śpiewam?"
    - Z zapominaniem tekstu i improwizacją
    
    Wygeneruj:
    1. Przerobiony tekst (1-2 zwrotki)
    2. Opis stylu wykonania
    3. Reakcję publiczności
    4. Specjalne efekty (np. "znaki zapytania", "chmury wątpliwości", "drżenie")
    """
    
    try:
        response = await ollama_service.generate_creative_content(prompt)
        
        return {
            "song_title": song["title"],
            "original_artist": song["artist"],
            "performer": "Wątpiący",
            "performance_style": "Niepewny Vibrato Mode",
            "lyrics": response[:500] + "...",
            "performance_score": random.uniform(4.0, 8.0),
            "audience_reaction": "Publiczność nie wie, czy śmiać się, czy współczuć... 🤔❓",
            "special_effects": ["Znaki zapytania", "Chmury wątpliwości", "Drżenie ekranu", "Echo"],
            "emoji_reactions": ["❓", "🤔", "😕", "🙃", "❓"]
        }
    except:
        return {
            "song_title": song["title"],
            "original_artist": song["artist"],
            "performer": "Wątpiący",
            "performance_style": "Niepewny Vibrato Mode",
            "lyrics": f"Może {song['title']}... ale nie jestem pewien... czy to jest dobry tekst? 🤔",
            "performance_score": 5.5,
            "audience_reaction": "Publiczność krzyczy 'dasz radę!' ale nikt nie jest pewien! ❓",
            "special_effects": ["Znaki zapytania", "Chmury wątpliwości"],
            "emoji_reactions": ["❓", "🤔", "😕"]
        }

def generate_encore_message(winner: str) -> str:
    """Generate encore message for karaoke winner"""
    
    encore_messages = {
        "Adam": "🌈 ADAM WYGRAŁ! Publiczność krzyczy 'ENCOOORE!' Tęcze eksplodują na scenie! ✨🎉",
        "Beata": "📊 BEATA TRIUMFUJE! Ktoś krzyknął 'ENCOOORE!' i natychmiast zaczął notować statystyki! 🔍📈",
        "Wątpiący": "❓ WĄTPIĄCY WYGRAŁ! Publiczność krzyczy 'ENCOOORE!'... czy na pewno? 🤔🎤"
    }
    
    return encore_messages.get(winner, "🎤 Zwycięzca! Bis! Bis!")

@router.get("/night-history")
async def get_karaoke_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get karaoke night history"""
    try:
        from app.database import DialogSession
        
        result = await db.execute(
            "SELECT * FROM dialog_sessions WHERE topic LIKE 'KARAOKE NIGHT:%' ORDER BY created_at DESC LIMIT {limit}"
        )
        nights = result.fetchall()
        
        night_history = []
        for night in nights:
            import json
            try:
                night_data = json.loads(night.messages)
                night_history.append({
                    "night_id": night.session_id,
                    "theme": night_data["theme"],
                    "participants": night_data["participants"],
                    "performances_completed": night_data["current_performance"],
                    "created_at": night.created_at.isoformat()
                })
            except:
                continue
        
        return {"nights": night_history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/song-suggestions")
async def get_song_suggestions():
    """Get song suggestions for karaoke"""
    
    song_suggestions = {
        "Pop": [
            {"title": "Shake It Off", "artist": "Taylor Swift", "difficulty": "Easy", "fun_factor": "High"},
            {"title": "Blinding Lights", "artist": "The Weeknd", "difficulty": "Medium", "fun_factor": "High"},
            {"title": "Dance Monkey", "artist": "Tones and I", "difficulty": "Easy", "fun_factor": "Very High"}
        ],
        "Disco": [
            {"title": "Stayin' Alive", "artist": "Bee Gees", "difficulty": "Medium", "fun_factor": "Extreme"},
            {"title": "Dancing Queen", "artist": "ABBA", "difficulty": "Easy", "fun_factor": "Very High"},
            {"title": "I Will Survive", "artist": "Gloria Gaynor", "difficulty": "Medium", "fun_factor": "High"}
        ],
        "Rock": [
            {"title": "Bohemian Rhapsody", "artist": "Queen", "difficulty": "Expert", "fun_factor": "Legendary"},
            {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses", "difficulty": "Hard", "fun_factor": "High"},
            {"title": "Livin' on a Prayer", "artist": "Bon Jovi", "difficulty": "Medium", "fun_factor": "Very High"}
        ],
        "Polish Hits": [
            {"title": "Małgośka", "artist": "Budka Suflera", "difficulty": "Medium", "fun_factor": "High"},
            {"title": "Chłop z Marsa", "artist": "De Mono", "difficulty": "Easy", "fun_factor": "Very High"},
            {"title": "Jesteś szalona", "artist": "Kasia Kowalska", "difficulty": "Medium", "fun_factor": "High"}
        ]
    }
    
    return {
        "song_suggestions": song_suggestions,
        "total_suggestions": sum(len(songs) for songs in song_suggestions.values()),
        "pro_tip": "🎤 Pro tip: Im bardziej absurdalne wykonanie, tym lepsza zabawa!",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/stage-stats")
async def get_stage_stats(db: AsyncSession = Depends(get_db)):
    """Get karaoke stage statistics"""
    try:
        from app.database import DialogSession
        
        # Total karaoke nights
        result = await db.execute(
            "SELECT COUNT(*) FROM dialog_sessions WHERE topic LIKE 'KARAOKE NIGHT:%'"
        )
        total_nights = result.scalar()
        
        return {
            "total_nights": total_nights or 0,
            "stage_ready": True,
            "spotlights_working": "✨",
            "microphone_quality": "🎤",
            "audience_capacity": "Unlimited! 🎪",
            "next_night_id": f"karaoke_{int(time.time())}",
            "stage_motto": "🎤 In music we trust! In absurdity we sing! 🎵",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))