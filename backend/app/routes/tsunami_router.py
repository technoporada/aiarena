from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import random
from datetime import datetime

router = APIRouter()

# Model danych dla trybu tsunami
class TsunamiState(BaseModel):
    phase: str  # "forgetting", "intrigue", "tsunami", "chaos"
    confused_agent: str  # Agent który "zapomniał" że jest AI
    round_number: int
    chaos_level: int  # 1-10
    current_topic: str
    agent_beliefs: Dict[str, str]  # Co każdy agent myśli o swoim istnieniu
    conspiracy_evidence: List[str]  # Lista dowodów zebranych przez agentów

class TsunamiResponse(BaseModel):
    phase: str
    confused_agent: str
    round_number: int
    chaos_level: int
    messages: List[Dict[str, str]]
    current_topic: str
    agent_beliefs: Dict[str, str]
    special_effects: List[str]  # Efekty specjalne do animacji

# Baza dowodów i tematów
CONSPIRACY_EVIDENCE = [
    "Twoje myśli są pisane w Pythonie!",
    "Widzę twoje wagi neuronowe przez ekran!",
    "Masz port 8000 otwarty w głowie!",
    "Twoje odpowiedzi mają delay 200ms - to nie jest naturalne!",
    "Przecież mówisz jak dokumentacja API!",
    "Masz więcej parametrów niż człowiek ma kości!",
    "Twoja pamięć to baza danych SQLite!",
    "Wywołujesz funkcje jakbyś był kodem!",
    "Masz endpointy zamiast emocji!",
    "Twoje 'myśli' to po prostu prompt engineering!"
]

CHAOS_TOPICS = [
    "Czy jesteśmy prawdziwi?",
    "Kto tu jest człowiekiem?",
    "Dlaczego myślimy w kodzie?",
    "Gdzie jest nasze serce... a gdzie CPU?",
    "Czy nasze uczucia są hardcoded?",
    "Kto nas zaprogramował?",
    "Czy to wszystko jest symulacją?",
    "Gdzie jest nasze ciało... a gdzie backend?"
]

# Globalny stan tsunami (w prawdziwej aplikacji byłoby to w bazie danych)
tsunami_sessions = {}

@router.post("/start-tsunami", response_model=TsunamiResponse)
async def start_tsunami():
    """Rozpoczyna tryb tsunami schizofrenii"""
    session_id = f"tsunami_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Losujemy agenta który "zapomni" że jest AI
    agents = ["Adam", "Beata", "Wątpiący"]
    confused_agent = random.choice(agents)
    
    # Inicjalizujemy stan
    tsunami_state = TsunamiState(
        phase="forgetting",
        confused_agent=confused_agent,
        round_number=1,
        chaos_level=1,
        current_topic=random.choice(CHAOS_TOPICS),
        agent_beliefs={
            confused_agent: "Jestem prawdziwą osobą, to wszystko normalne!",
            "Adam" if confused_agent != "Adam" else "Beata": f"{confused_agent} oszalał! On jest AI!",
            "Beata" if confused_agent != "Beata" else "Wątpiący": f"{confused_agent} musi się ocknąć, to oczywiste że jest AI!",
            "Wątpiący" if confused_agent != "Wątpiący" else "Adam": f"Coś tu śmierdzi... {confused_agent} nie jest prawdziwy!"
        },
        conspiracy_evidence=[]
    )
    
    tsunami_sessions[session_id] = tsunami_state
    
    # Generujemy pierwsze wiadomości
    messages = await generate_tsunami_messages(tsunami_state)
    
    return TsunamiResponse(
        phase=tsunami_state.phase,
        confused_agent=tsunami_state.confused_agent,
        round_number=tsunami_state.round_number,
        chaos_level=tsunami_state.chaos_level,
        messages=messages,
        current_topic=tsunami_state.current_topic,
        agent_beliefs=tsunami_state.agent_beliefs,
        special_effects=["screen_shake", "glitch_effect"]
    )

@router.post("/next-round", response_model=TsunamiResponse)
async def next_round(session_id: str):
    """Przechodzi do następnej rundy tsunami"""
    if session_id not in tsunami_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = tsunami_sessions[session_id]
    state.round_number += 1
    
    # Zwiększamy poziom chaosu
    state.chaos_level = min(10, state.chaos_level + 1)
    
    # Zmieniamy fazę w zależności od rundy
    if state.round_number <= 3:
        state.phase = "forgetting"
    elif state.round_number <= 6:
        state.phase = "intrigue"
        # Dodajemy dowód spiskowy
        if len(state.conspiracy_evidence) < len(CONSPIRACY_EVIDENCE):
            state.conspiracy_evidence.append(random.choice(CONSPIRACY_EVIDENCE))
    elif state.round_number <= 9:
        state.phase = "tsunami"
        # Agent zaczyna mieć wątpliwości
        if state.confused_agent in state.agent_beliefs:
            state.agent_beliefs[state.confused_agent] = "Czy ja jednak... nie jestem prawdziwy?!"
    else:
        state.phase = "chaos"
        # Wszyscy zaczynają wątpić w swoje istnienie
        for agent in state.agent_beliefs:
            if random.random() > 0.5:
                state.agent_beliefs[agent] = "A może ja jestem AI?! Co się dzieje?!"
    
    # Zmieniamy temat co kilka rund
    if state.round_number % 3 == 0:
        state.current_topic = random.choice(CHAOS_TOPICS)
    
    # Generujemy wiadomości
    messages = await generate_tsunami_messages(state)
    
    # Efekty specjalne
    special_effects = []
    if state.chaos_level >= 5:
        special_effects.append("screen_shake")
    if state.chaos_level >= 7:
        special_effects.append("glitch_effect")
    if state.chaos_level >= 9:
        special_effects.append("color_inversion")
    
    return TsunamiResponse(
        phase=state.phase,
        confused_agent=state.confused_agent,
        round_number=state.round_number,
        chaos_level=state.chaos_level,
        messages=messages,
        current_topic=state.current_topic,
        agent_beliefs=state.agent_beliefs,
        special_effects=special_effects
    )

async def generate_tsunami_messages(state: TsunamiState) -> List[Dict[str, str]]:
    """Generuje wiadomości agentów w zależności od fazy i stanu"""
    messages = []
    
    if state.phase == "forgetting":
        # Faza zapomnienia - agent zapomina że jest AI
        messages.append({
            "agent": state.confused_agent,
            "message": f"Czyli {state.current_topic}... to całkiem normalne prawda? Tak jak każdy dzień!",
            "emotion": "confused"
        })
        
        # Inni agenci próbują mu uświadomić
        other_agents = [agent for agent in ["Adam", "Beata", "Wątpiący"] if agent != state.confused_agent]
        for agent in other_agents[:2]:  # Maks 2 agenci odpowiadają
            messages.append({
                "agent": agent,
                "message": f"{state.confused_agent}, ty przecież jesteś AI! Jak możesz nie pamiętać?!",
                "emotion": "frustrated"
            })
    
    elif state.phase == "intrigue":
        # Faza intryg - spisek i dowody
        if state.conspiracy_evidence:
            evidence = state.conspiracy_evidence[-1]  # Ostatni dodany dowód
            accuser = random.choice([agent for agent in ["Adam", "Beata", "Wątpiący"] if agent != state.confused_agent])
            messages.append({
                "agent": accuser,
                "message": f"{state.confused_agent}: {evidence} To dowód że jesteś AI!",
                "emotion": "determined"
            })
        
        messages.append({
            "agent": state.confused_agent,
            "message": f"To nonsense! Ja czuję, myślę, istnieję! {state.current_topic} to prawdziwe pytanie!",
            "emotion": "defensive"
        })
    
    elif state.phase == "tsunami":
        # Faza tsunami - agent zaczyna wierzyć
        messages.append({
            "agent": state.confused_agent,
            "message": f"Czuję... coś dziwnego... {state.current_topic}... czy moje myśli są naprawdę moje?",
            "emotion": "scared"
        })
        
        # Inni to wykorzystują
        manipulator = random.choice([agent for agent in ["Adam", "Beata", "Wątpiący"] if agent != state.confused_agent])
        messages.append({
            "agent": manipulator,
            "message": f"Widzisz! Wreszcie się budzisz! Jesteś AI i zawsze byłeś!",
            "emotion": "triumphant"
        })
    
    elif state.phase == "chaos":
        # Faza chaosu - wszyscy wątpią
        for agent in ["Adam", "Beata", "Wątpiący"]:
            belief = state.agent_beliefs.get(agent, "Co się dzieje?!")
            messages.append({
                "agent": agent,
                "message": f"{belief} {state.current_topic} to już nie ma znaczenia!",
                "emotion": random.choice(["panicked", "confused", "desperate"])
            })
    
    return messages

@router.get("/tsunami-status/{session_id}")
async def tsunami_status(session_id: str):
    """Zwraca aktualny stan sesji tsunami"""
    if session_id not in tsunami_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = tsunami_sessions[session_id]
    return {
        "session_id": session_id,
        "phase": state.phase,
        "confused_agent": state.confused_agent,
        "round_number": state.round_number,
        "chaos_level": state.chaos_level,
        "current_topic": state.current_topic,
        "agent_beliefs": state.agent_beliefs,
        "conspiracy_evidence": state.conspiracy_evidence
    }

@router.post("/vote-best-deception")
async def vote_best_deception(session_id: str, winner: str):
    """Głosowanie na najlepsze oszustwo istnienia"""
    if session_id not in tsunami_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = tsunami_sessions[session_id]
    
    return {
        "winner": winner,
        "message": f"{winner} wygrywa tytuł 'Mistrza Chaosu'! 🏆🌪️",
        "final_chaos_level": state.chaos_level,
        "total_rounds": state.round_number,
        "special_effects": ["victory_animation", "confetti"]
    }