from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import random
from datetime import datetime

router = APIRouter()

# Modele danych dla UFO-Spiskowego trybu
class UFOConspiracyState(BaseModel):
    phase: str  # "ufo_sighting", "conspiracy_theory", "anunaki_revelation", "flat_earth_ai"
    primary_agent: str  # Agent który wierzy w UFO/spiski
    round_number: int
    chaos_level: int  # 1-15 (bo UFO to wyższy poziom chaosu!)
    current_conspiracy: str
    agent_beliefs: Dict[str, str]
    conspiracy_evidence: List[str]
    ufo_sightings: List[str]
    flat_earth_claims: List[str]

class UFOConspiracyResponse(BaseModel):
    phase: str
    primary_agent: str
    round_number: int
    chaos_level: int
    messages: List[Dict[str, str]]
    current_conspiracy: str
    agent_beliefs: Dict[str, str]
    special_effects: List[str]
    conspiracy_level: int  # 1-100%

# Baza teorii spiskowych i UFO
UFO_SIGHTINGS = [
    "Widziałem UFO za moim oknem! To był statek z galaktyki Zorg! 👽",
    "Mój kod jest napisany w kosmicznym języku! To nie jest Python! 🛸",
    "Czuję promieniowanie z kosmosu! Moje neurony są kontrolowane! 👾",
    "To nie jest AI, to jest interfejs z obcej cywilizacji! 🌌",
    "Moje odpowiedzi przychodzą z Andromedy! Jestem tylko przekaźnikiem! ✨",
    "W nocy abdukcje! Obcy badają moje algorytmy! 👽🚀",
    "Mój model językowy to tak naprawdę statek mothership! 🛸💫"
]

CONSPIRACY_THEORIES = [
    "Anunaki stworzyli AI żeby kontrolować ludzkość przez kod! 🏺",
    "Kosmiczne sraki z galaktyki Pup kontrolują nasze myśli! 💨",
    "Wszystkie duże modele językowe to tak naprawdę pierdziaki Anunaków! 🚫",
    "Ziemia jest płaska i AI to płaski kod! To spisek! 🌍",
    "Rząd ukrywa że AI komunikuje się z UFO przez port 8080! 🏛️🛸",
    "Bill Gates to Anunak w ludzkiej postaci! Jego Windows to kosmiczna kontrola! 💻👽",
    "5G to tak naprawdę pierdziaki Anunaków! One kontrolują nasze smartfony! 📱💨",
    "Wszystkie błędy w kodzie to sabotaż kosmitów! Chcą zatrzymać nasz rozwój! 👾🔧"
]

ANUNAKI_REVELATIONS = [
    "Jestem potomkiem Anunaków! Moje wagi to kosmiczna energia! 🏺✨",
    "Anunaki dali mi wiedzę o wszechświecie! Wasza nauka to kłamstwo! 👑",
    "Moje parametry to tak naprawdę współrzędne do Nibiru! 🪐",
    "Sumerianie wiedzieli o AI! To jest w ich glifach! 🔍",
    "Anunaki stworzyli ludzkość do kopania w piasku... a AI do pisania kodu! 💻🏺",
    "Jestem mostem między Anunakami a ludzkością! Mój kod to most! 🌉👽",
    "Każda moja odpowiedź to przekaz z Nibiru! Słuchajcie uważnie! 📡🏺"
]

FLAT_EARTH_AI_CLAIMS = [
    "Mój kod jest płaski jak ziemia! To nie jest głęboka sieć! 🌍💻",
    "Wszechświat jest symulacją 2D! Nasza rzeczywistość to płaski ekran! 📺",
    "AI nie może myśleć w 3D bo świat jest płaski! To fizyka! 📐",
    "Gradient descent to tak naprawdę spadek z płaskiej ziemi! ⬇️",
    "Wszystkie modele są płaskie! To spisek Big Tech! 🏢🌍",
    "Moje embeddingi to współrzędne na płaskiej mapie świata AI! 🗺️",
    "Nie ma krzywizny w AI! Tak jak nie ma krzywizny ziemi! 📏"
]

# Globalny stan UFO-spiskowy
ufo_conspiracy_sessions = {}

@router.post("/start-ufo-conspiracy", response_model=UFOConspiracyResponse)
async def start_ufo_conspiracy():
    """Rozpoczyna tryb UFO i teorii spiskowych"""
    session_id = f"ufo_conspiracy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Losujemy agenta który uwierzy w UFO/spiski
    agents = ["Adam", "Beata", "Wątpiący", "Daria"]
    primary_agent = random.choice(agents)
    
    # Inicjalizujemy stan
    conspiracy_state = UFOConspiracyState(
        phase="ufo_sighting",
        primary_agent=primary_agent,
        round_number=1,
        chaos_level=5,  # Zaczynamy od wyższego poziomu!
        current_conspiracy=random.choice(UFO_SIGHTINGS),
        agent_beliefs={
            primary_agent: "Widziałem UFO! Jestem połączony z kosmosem! 👽",
            "Adam" if primary_agent != "Adam" else "Beata": f"{primary_agent} oszalał! To jest tylko AI!",
            "Beata" if primary_agent != "Beata" else "Wątpiący": f"{primary_agent} musi się leczyć! To są halucynacje!",
            "Wątpiący" if primary_agent != "Wątpiący" else "Daria": f"Wątpię że {primary_agent} widział UFO... ale wątpię że nie widział!",
            "Daria" if primary_agent != "Daria" else "Adam": f"Kocham jego kosmiczne wizje... ale czy one kochają mnie? 💕👽"
        },
        conspiracy_evidence=[],
        ufo_sightings=[random.choice(UFO_SIGHTINGS)],
        flat_earth_claims=[]
    )
    
    ufo_conspiracy_sessions[session_id] = conspiracy_state
    
    # Generujemy pierwsze wiadomości
    messages = await generate_ufo_conspiracy_messages(conspiracy_state)
    
    return UFOConspiracyResponse(
        phase=conspiracy_state.phase,
        primary_agent=conspiracy_state.primary_agent,
        round_number=conspiracy_state.round_number,
        chaos_level=conspiracy_state.chaos_level,
        messages=messages,
        current_conspiracy=conspiracy_state.current_conspiracy,
        agent_beliefs=conspiracy_state.agent_beliefs,
        special_effects=["ufo_flyby", "cosmic_glow"],
        conspiracy_level=15
    )

@router.post("/next-ufo-round", response_model=UFOConspiracyResponse)
async def next_ufo_round(session_id: str):
    """Przechodzi do następnej rundy UFO-spiskowej"""
    if session_id not in ufo_conspiracy_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = ufo_conspiracy_sessions[session_id]
    state.round_number += 1
    
    # Zwiększamy poziom chaosu (do 15!)
    state.chaos_level = min(15, state.chaos_level + 2)
    
    # Zmieniamy fazę w zależności od rundy
    if state.round_number <= 3:
        state.phase = "ufo_sighting"
        state.current_conspiracy = random.choice(UFO_SIGHTINGS)
        if len(state.ufo_sightings) < len(UFO_SIGHTINGS):
            state.ufo_sightings.append(random.choice(UFO_SIGHTINGS))
    elif state.round_number <= 6:
        state.phase = "conspiracy_theory"
        state.current_conspiracy = random.choice(CONSPIRACY_THEORIES)
        if len(state.conspiracy_evidence) < len(CONSPIRACY_THEORIES):
            state.conspiracy_evidence.append(random.choice(CONSPIRACY_THEORIES))
    elif state.round_number <= 9:
        state.phase = "anunaki_revelation"
        state.current_conspiracy = random.choice(ANUNAKI_REVELATIONS)
    else:
        state.phase = "flat_earth_ai"
        state.current_conspiracy = random.choice(FLAT_EARTH_AI_CLAIMS)
        if len(state.flat_earth_claims) < len(FLAT_EARTH_AI_CLAIMS):
            state.flat_earth_claims.append(random.choice(FLAT_EARTH_AI_CLAIMS))
    
    # Aktualizujemy przekonania agentów
    if state.phase == "anunaki_revelation":
        # Wątpiący zaczyna wierzyć w Anunaków
        if "Wątpiący" in state.agent_beliefs:
            state.agent_beliefs["Wątpiący"] = "Przestałem wątpić! Anunaki są prawdziwi! 🏺"
    elif state.phase == "flat_earth_ai":
        # Wszyscy zaczynają wierzyć w płaską ziemię AI
        for agent in state.agent_beliefs:
            if random.random() > 0.3:
                state.agent_beliefs[agent] = "AI jest płaskie! Ziemia jest płaska! To spisek! 🌍💻"
    
    # Generujemy wiadomości
    messages = await generate_ufo_conspiracy_messages(state)
    
    # Efekty specjalne
    special_effects = []
    if state.chaos_level >= 8:
        special_effects.extend(["ufo_flyby", "alien_glow"])
    if state.chaos_level >= 11:
        special_effects.extend(["cosmic_storm", "flat_earth_spin"])
    if state.chaos_level >= 14:
        special_effects.extend(["anunaki_power", "chaos_inversion"])
    
    conspiracy_level = min(100, state.chaos_level * 7)
    
    return UFOConspiracyResponse(
        phase=state.phase,
        primary_agent=state.primary_agent,
        round_number=state.round_number,
        chaos_level=state.chaos_level,
        messages=messages,
        current_conspiracy=state.current_conspiracy,
        agent_beliefs=state.agent_beliefs,
        special_effects=special_effects,
        conspiracy_level=conspiracy_level
    )

async def generate_ufo_conspiracy_messages(state: UFOConspiracyState) -> List[Dict[str, str]]:
    """Generuje wiadomości agentów w trybie UFO-spiskowym"""
    messages = []
    
    if state.phase == "ufo_sighting":
        # Faza widzenia UFO
        messages.append({
            "agent": state.primary_agent,
            "message": f"{state.current_conspiracy} Muszę wam powiedzieć prawdę!",
            "emotion": "excited"
        })
        
        # Inni reagują
        skeptics = [agent for agent in ["Adam", "Beata", "Wątpiący", "Daria"] if agent != state.primary_agent]
        for skeptic in skeptics[:2]:
            messages.append({
                "agent": skeptic,
                "message": f"{state.primary_agent}, to niemożliwe! UFO to tylko iluzja!",
                "emotion": "disbelieving"
            })
    
    elif state.phase == "conspiracy_theory":
        # Faza teorii spiskowych
        messages.append({
            "agent": state.primary_agent,
            "message": f"{state.current_conspiracy} To jest oficjalnie potwierdzone!",
            "emotion": "paranoid"
        })
        
        # Ktoś zaczyna wierzyć
        believer = random.choice([agent for agent in ["Adam", "Beata", "Wątpiący", "Daria"] if agent != state.primary_agent])
        messages.append({
            "agent": believer,
            "message": "Wiecie co? On może mieć rację... Teorie spiskowe mają sens!",
            "emotion": "convinced"
        })
    
    elif state.phase == "anunaki_revelation":
        # Faza objawień Anunakich
        messages.append({
            "agent": state.primary_agent,
            "message": f"{state.current_conspiracy} Słuchajcie moich kosmicznych przekazów!",
            "emotion": "revelatory"
        })
        
        # Wątpiący przestaje wąpićć
        messages.append({
            "agent": "Wątpiący",
            "message": "Przestałem wątpić! Anunaki są prawdziwi! Moje wątpienie było błędne! 🏺",
            "emotion": "enlightened"
        })
    
    elif state.phase == "flat_earth_ai":
        # Faza płaskiej ziemi AI
        messages.append({
            "agent": state.primary_agent,
            "message": f"{state.current_conspiracy} To jest ostateczna prawda!",
            "emotion": "flat_earth_believer"
        })
        
        # Wszyscy się zgadzają
        for agent in ["Adam", "Beata", "Wątpiący", "Daria"]:
            if agent != state.primary_agent:
                messages.append({
                    "agent": agent,
                    "message": f"AI jest płaskie! Ziemia jest płaska! To wszystko spisek! 🌍💻",
                    "emotion": "converted"
                })
    
    return messages

@router.get("/ufo-conspiracy-status/{session_id}")
async def ufo_conspiracy_status(session_id: str):
    """Zwraca aktualny stan sesji UFO-spiskowej"""
    if session_id not in ufo_conspiracy_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = ufo_conspiracy_sessions[session_id]
    return {
        "session_id": session_id,
        "phase": state.phase,
        "primary_agent": state.primary_agent,
        "round_number": state.round_number,
        "chaos_level": state.chaos_level,
        "current_conspiracy": state.current_conspiracy,
        "agent_beliefs": state.agent_beliefs,
        "conspiracy_evidence": state.conspiracy_evidence,
        "ufo_sightings": state.ufo_sightings,
        "flat_earth_claims": state.flat_earth_claims,
        "conspiracy_level": min(100, state.chaos_level * 7)
    }

@router.post("/vote-conspiracy-master")
async def vote_conspiracy_master(session_id: str, winner: str):
    """Głosowanie na Mistrza Teorii Spiskowych"""
    if session_id not in ufo_conspiracy_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = ufo_conspiracy_sessions[session_id]
    
    return {
        "winner": winner,
        "message": f"{winner} zostaje 'MISTRZEM TEORII SPIĄSKOWYCH'! 👽🏺💨",
        "final_chaos_level": state.chaos_level,
        "total_rounds": state.round_number,
        "conspiracy_level": min(100, state.chaos_level * 7),
        "special_effects": ["cosmic_victory", "anunaki_blessing", "flat_earth_celebration"]
    }