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

class GladiatorBattleRequest(BaseModel):
    topic: str
    agent1: str = "Adam"
    agent2: str = "Beata"
    max_rounds: int = 5
    absurdity_start_level: float = 0.1

class GladiatorRound(BaseModel):
    round_number: int
    agent1_attack: str
    agent2_attack: str
    absurdity_level: float
    round_topic: str
    winner: str
    voter_count: int

class GladiatorBattle(BaseModel):
    battle_id: str
    topic: str
    agent1: str
    agent2: str
    rounds: List[GladiatorRound]
    final_winner: str
    total_absurdity: float
    battle_duration: float
    created_at: str

class VoteRequest(BaseModel):
    battle_id: str
    round_number: int
    voted_agent: str
    voter_id: str

@router.post("/start-battle")
async def start_gladiator_battle(
    request: GladiatorBattleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start a gladiator battle between two agents"""
    try:
        battle_id = f"gladiator_{int(time.time())}"
        start_time = time.time()
        
        # Initialize battle
        battle_data = {
            "battle_id": battle_id,
            "topic": request.topic,
            "agent1": request.agent1,
            "agent2": request.agent2,
            "rounds": [],
            "current_round": 0,
            "absurdity_level": request.absurdity_start_level,
            "votes": {},
            "start_time": start_time
        }
        
        # Store battle in database
        from app.database import DialogSession
        battle_session = DialogSession(
            session_id=battle_id,
            agent1_name=request.agent1,
            agent2_name=request.agent2,
            topic=f"GLADIATOR BATTLE: {request.topic}",
            messages=str(battle_data),
            drama_level=request.absurdity_start_level
        )
        db.add(battle_session)
        await db.commit()
        
        return {
            "battle_id": battle_id,
            "message": f"⚔️ Gladiator Battle started between {request.agent1} and {request.agent2}!",
            "topic": request.topic,
            "max_rounds": request.max_rounds,
            "arena_ready": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next-round")
async def next_gladiator_round(
    battle_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Generate next round of gladiator battle"""
    try:
        # Get battle data
        from app.database import DialogSession
        result = await db.execute(
            f"SELECT * FROM dialog_sessions WHERE session_id = '{battle_id}'"
        )
        battle_session = result.fetchone()
        
        if not battle_session:
            raise HTTPException(status_code=404, detail="Battle not found")
        
        import json
        battle_data = json.loads(battle_session.messages)
        
        # Check if battle is finished
        if battle_data["current_round"] >= 5:  # max rounds
            return await finish_gladiator_battle(battle_id, db)
        
        # Generate round
        round_number = battle_data["current_round"] + 1
        absurdity_level = battle_data["absurdity_level"]
        
        # Create round-specific topic with absurdity
        round_topic = generate_absurd_topic(battle_data["topic"], absurdity_level, round_number)
        
        # Generate attacks
        agent1_attack = await generate_gladiator_attack(
            battle_data["agent1"], 
            battle_data["agent2"], 
            round_topic, 
            absurdity_level
        )
        
        agent2_attack = await generate_gladiator_attack(
            battle_data["agent2"], 
            battle_data["agent1"], 
            round_topic, 
            absurdity_level
        )
        
        # Create round data
        round_data = {
            "round_number": round_number,
            "agent1_attack": agent1_attack,
            "agent2_attack": agent2_attack,
            "absurdity_level": absurdity_level,
            "round_topic": round_topic,
            "votes": {"agent1": 0, "agent2": 0},
            "winner": None
        }
        
        battle_data["rounds"].append(round_data)
        battle_data["current_round"] = round_number
        battle_data["absurdity_level"] = min(absurdity_level + 0.2, 1.0)  # Increase absurdity
        
        # Update battle in database
        battle_session.messages = str(battle_data)
        battle_session.drama_level = battle_data["absurdity_level"]
        await db.commit()
        
        return {
            "round_number": round_number,
            "round_topic": round_topic,
            "agent1_attack": agent1_attack,
            "agent2_attack": agent2_attack,
            "absurdity_level": absurdity_level,
            "battle_status": "voting_open",
            "voting_time_limit": 30  # 30 seconds to vote
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vote")
async def vote_for_round(
    request: VoteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Vote for the winner of a round"""
    try:
        # Get battle data
        from app.database import DialogSession
        result = await db.execute(
            f"SELECT * FROM dialog_sessions WHERE session_id = '{request.battle_id}'"
        )
        battle_session = result.fetchone()
        
        if not battle_session:
            raise HTTPException(status_code=404, detail="Battle not found")
        
        import json
        battle_data = json.loads(battle_session.messages)
        
        # Find the round
        current_round = None
        for round_data in battle_data["rounds"]:
            if round_data["round_number"] == request.round_number:
                current_round = round_data
                break
        
        if not current_round:
            raise HTTPException(status_code=404, detail="Round not found")
        
        # Record vote
        if request.voted_agent in ["agent1", "agent2"]:
            current_round["votes"][request.voted_agent] += 1
        
        # Check if voting should end (simple threshold for demo)
        total_votes = current_round["votes"]["agent1"] + current_round["votes"]["agent2"]
        if total_votes >= 3:  # Minimum votes to end round
            # Determine winner
            if current_round["votes"]["agent1"] > current_round["votes"]["agent2"]:
                current_round["winner"] = "agent1"
            elif current_round["votes"]["agent2"] > current_round["votes"]["agent1"]:
                current_round["winner"] = "agent2"
            else:
                current_round["winner"] = "tie"
            
            # Update battle data
            battle_session.messages = str(battle_data)
            await db.commit()
            
            return {
                "round_finished": True,
                "winner": current_round["winner"],
                "votes": current_round["votes"],
                "next_round_available": battle_data["current_round"] < 5
            }
        
        return {
            "vote_recorded": True,
            "current_votes": current_round["votes"],
            "round_finished": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def finish_gladiator_battle(battle_id: str, db: AsyncSession):
    """Finish the gladiator battle and determine final winner"""
    try:
        # Get battle data
        from app.database import DialogSession
        result = await db.execute(
            f"SELECT * FROM dialog_sessions WHERE session_id = '{battle_id}'"
        )
        battle_session = result.fetchone()
        
        import json
        battle_data = json.loads(battle_session.messages)
        
        # Count wins
        agent1_wins = sum(1 for round_data in battle_data["rounds"] if round_data.get("winner") == "agent1")
        agent2_wins = sum(1 for round_data in battle_data["rounds"] if round_data.get("winner") == "agent2")
        
        # Determine final winner
        if agent1_wins > agent2_wins:
            final_winner = battle_data["agent1"]
        elif agent2_wins > agent1_wins:
            final_winner = battle_data["agent2"]
        else:
            final_winner = "tie"
        
        # Calculate battle duration
        battle_duration = time.time() - battle_data["start_time"]
        
        # Mark battle as finished
        battle_session.is_active = False
        battle_session.messages = str(battle_data)
        await db.commit()
        
        return {
            "battle_finished": True,
            "final_winner": final_winner,
            "agent1_wins": agent1_wins,
            "agent2_wins": agent2_wins,
            "total_absurdity": battle_data["absurdity_level"],
            "battle_duration": battle_duration,
            "victory_message": generate_victory_message(final_winner, battle_data["agent1"], battle_data["agent2"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_absurd_topic(base_topic: str, absurdity_level: float, round_number: int) -> str:
    """Generate increasingly absurd topics"""
    
    absurd_modifiers = [
        "w kosmicznym wymiarze",
        "z perspektywy kota",
        "jakby to opowiedział dziecko",
        "w stylu science fiction",
        "z przymrużeniem oka szalonego naukowca",
        "jakby to było w bajce Disneya",
        "w alternatywnej rzeczywistości",
        "z punktu widzenia obcego cywilizacji"
    ]
    
    if absurdity_level < 0.3:
        return base_topic
    elif absurdity_level < 0.6:
        modifier = random.choice(absurd_modifiers[:3])
        return f"{base_topic} {modifier}"
    else:
        modifier1 = random.choice(absurd_modifiers)
        modifier2 = random.choice(["z dodatkowym absurdem", "w wersji ekstremalnej", "na sterydach"])
        return f"{base_topic} {modifier1} {modifier2}"

async def generate_gladiator_attack(
    attacker: str, 
    defender: str, 
    topic: str, 
    absurdity_level: float
) -> str:
    """Generate a gladiator attack/riposte"""
    
    ollama_service = OllamaService()
    
    if attacker == "Adam":
        prompt = f"""
        Jesteś Adamem - optymistycznym gladiatorem! Atakujesz {defender} na arenie!
        Temat rundy: {topic}
        Poziom absurdu: {absurdity_level} (im wyższy, tym bardziej absurdalnie!)
        
        Twoj atak powinien być:
        - Pełen entuzjazmu i optymizmu
        - Zawierać mocne argumenty (nawet absurdalne)
        - Być agresywny ale w pozytywny sposób
        - Używać wykrzykników i pozytywnych słów
        - Jeśli absurdity_level > 0.5, być kompletnie absurdalny!
        
        Twój atak (krótki, mocny, zadziwiający):
        """
    elif attacker == "Beata":
        prompt = f"""
        Jesteś Beatą - sceptyczną gladiatorką! Atakujesz {defender} na arenie!
        Temat rundy: {topic}
        Poziom absurdu: {absurdity_level} (im wyższy, tym bardziej absurdalnie!)
        
        Twój atak powinien być:
        - Analityczny i pełen logiki (nawet jeśli absurdalnej)
        - Zawierać sceptyczne argumenty
        - Być precyzyjny i techniczny
        - Zadawać retoryczne pytania
        - Jeśli absurdity_level > 0.5, używać pseudonaukowych terminów!
        
        Twój atak (krótki, celny, zadziwiający):
        """
    else:  # Wątpiący
        prompt = f"""
        Jesteś Wątpiącym - niezdecydowanym gladiatorem! Atakujesz {defender} na arenie!
        Temat rundy: {topic}
        Poziom absurdu: {absurdity_level} (im wyższy, tym bardziej absurdalnie!)
        
        Twój atak powinien być:
        - Pełen wątpliwości i niepewności
        - Zawierać pytania i alternatywne perspektywy
        - Być niepodejmujący ostatecznych decyzji
        - Używać zwrotów typu "może", "prawdopodobnie"
        - Jeśli absurdity_level > 0.5, być kompletnie zagubiony!
        
        Twój atak (krótki, pełen wątpliwości, zadziwiający):
        """
    
    try:
        attack = await ollama_service.generate_creative_content(prompt)
        return attack.strip()
    except:
        # Fallback attacks
        fallback_attacks = {
            "Adam": [
                f"{topic} to jest NIESAMOWITE! {defender} nie ma szans! ✨",
                f"Mój optymizm pokona Twój sceptycyzm, {defender}! 🌈",
                f"{topic} + moja energia = VICTORY! 🏆"
            ],
            "Beata": [
                f"Statystycznie mówiąc, {topic} dowodzi mojej racji! {defender}! 📊",
                f"Twoje argumenty są iluzoryczne, {defender}! 🔍",
                f"Analiza temat {topic} pokazuje Twoją porażkę! 📈"
            ],
            "Wątpiący": [
                f"Może {topic}... ale czy na pewno? {defender}... 🤔",
                f"Nie jestem pewien co do {topic}, ale {defender} jest gorszy... ❓",
                f"Prawdopodobnie {topic}, ale może nie... {defender} przegrywa! 😕"
            ]
        }
        
        return random.choice(fallback_attacks.get(attacker, ["Atak!"]))

def generate_victory_message(winner: str, agent1: str, agent2: str) -> str:
    """Generate victory message"""
    
    if winner == "tie":
        return "🤝 REMIS! Obaj gladiatorzy są równie silni! Areny drżą z podziwu!"
    
    victory_messages = {
        "Adam": [
            "🌈 ADAM ZWYCIĘŻA! Optymizm pokonał wszystko! Tęcze eksplodują na arenie! ✨",
            "🏆 ADAM MISTRZ! Jego pozytywna energia rozbroiła przeciwnika! 🎉",
            "⚡ ADAM NIE DO ZATRZYMANIA! Entuzjazm triumfuje! 🌟"
        ],
        "Beata": [
            "🔍 BEATA ZWYCIĘŻA! Logika i analiza pokonały emocje! 📊",
            "📈 BEATA TRIUMFUJE! Statystyki nie kłamią! 🎯",
            "🧠 BEATA MISTRZOWI! Jej sceptycyzm okazał się bronią! 🔬"
        ],
        "Wątpiący": [
            "❓ WĄTPIĄCY ZWYCIĘŻA! Może... prawdopodobnie... na pewno! 🤔",
            "🎯 WĄTPIĄCY TRIUMFUJE! Jego niepewność okazała się strategią! 😕",
            "🏆 WĄTPIĄCY MISTRZ! Wątpliwości są siłą! ❓"
        ]
    }
    
    return random.choice(victory_messages.get(winner, ["Zwycięzca!"]))

@router.get("/battle-history")
async def get_battle_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get gladiator battle history"""
    try:
        from app.database import DialogSession
        
        result = await db.execute(
            f"SELECT * FROM dialog_sessions WHERE topic LIKE 'GLADIATOR BATTLE:%' ORDER BY created_at DESC LIMIT {limit}"
        )
        battles = result.fetchall()
        
        battle_history = []
        for battle in battles:
            import json
            try:
                battle_data = json.loads(battle.messages)
                battle_history.append({
                    "battle_id": battle.session_id,
                    "topic": battle_data["topic"],
                    "agent1": battle_data["agent1"],
                    "agent2": battle_data["agent2"],
                    "rounds_completed": battle_data["current_round"],
                    "final_absurdity": battle_data["absurdity_level"],
                    "created_at": battle.created_at.isoformat()
                })
            except:
                continue
        
        return {"battles": battle_history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/arena-stats")
async def get_arena_stats(db: AsyncSession = Depends(get_db)):
    """Get gladiator arena statistics"""
    try:
        from app.database import DialogSession
        
        # Total battles
        result = await db.execute(
            "SELECT COUNT(*) FROM dialog_sessions WHERE topic LIKE 'GLADIATOR BATTLE:%'"
        )
        total_battles = result.scalar()
        
        # Most wins by agent
        # This is simplified - in real implementation you'd parse battle data
        return {
            "total_battles": total_battles or 0,
            "arena_active": True,
            "next_battle_id": f"gladiator_{int(time.time())}",
            "arena_motto": "⚔️ In absurdity we trust! In absurdity we fight! ⚔️",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))