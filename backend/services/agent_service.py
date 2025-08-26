import asyncio
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from services.ollama_service import OllamaService

class SplitDialogAgent:
    """Agent that generates dialog between two different AI personalities"""
    
    def __init__(self):
        self.ollama_service = OllamaService()
        self.agents = {
            "Adam": {
                "personality": "optymistyczny i pełen entuzjazmu",
                "style": "używa emoji, wykrzykników, pozytywnych słów",
                "emoji": "😊",
                "color": "blue"
            },
            "Beata": {
                "personality": "sceptyczna i analityczna", 
                "style": "zadaje pytania, analizuje, jest rzeczowa",
                "emoji": "🔍",
                "color": "red"
            }
        }
    
    async def generate_dialog(self, topic: str, max_turns: int = 5) -> List[Dict[str, Any]]:
        """Generate a dialog between Adam and Beata"""
        dialog = []
        
        # Starting message
        current_agent = "Adam"
        context = f"Rozmawiacie na temat: {topic}"
        
        for turn in range(max_turns):
            # Generate response from current agent
            response = await self._generate_agent_response(
                topic, current_agent, context, dialog
            )
            
            # Add to dialog
            dialog.append({
                "agent": current_agent,
                "text": response,
                "timestamp": datetime.now().isoformat(),
                "turn": turn + 1
            })
            
            # Switch agent
            current_agent = "Beata" if current_agent == "Adam" else "Adam"
            
            # Update context
            context = f"Ostatnia odpowiedź: {response}"
        
        return dialog
    
    async def generate_dramatic_dialog(
        self, 
        topic: str, 
        duration: int = 60, 
        drama_level: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Generate dramatic dialog for Reality Show Mode"""
        dialog = []
        start_time = time.time()
        
        current_agent = "Adam"
        context = f"Reality Show! Rozmawiacie na temat: {topic}. Bądźcie dramatyczni!"
        
        turn = 0
        while time.time() - start_time < duration:
            turn += 1
            
            # Generate dramatic response
            response = await self._generate_dramatic_response(
                topic, current_agent, context, dialog, drama_level
            )
            
            # Add drama indicators
            drama_indicators = self._get_drama_indicators(drama_level)
            
            dialog.append({
                "agent": current_agent,
                "text": response,
                "timestamp": datetime.now().isoformat(),
                "turn": turn,
                "drama_score": random.uniform(0.3, 1.0),
                "emotion": drama_indicators["emotion"],
                "emoji": drama_indicators["emoji"]
            })
            
            # Switch agent
            current_agent = "Beata" if current_agent == "Adam" else "Adam"
            
            # Update context with dramatic elements
            context = f"Ostatnia odpowiedź (DRAMATYCZNA): {response}"
            
            # Add some delay for realism
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return dialog
    
    async def _generate_agent_response(
        self, 
        topic: str, 
        agent_name: str, 
        context: str, 
        previous_dialog: List[Dict]
    ) -> str:
        """Generate response from specific agent"""
        
        agent_config = self.agents[agent_name]
        
        # Build conversation history
        history = ""
        for msg in previous_dialog[-3:]:  # Last 3 messages
            history += f"{msg['agent']}: {msg['text']}\n"
        
        prompt = f"""
        Jesteś {agent_name} - {agent_config['personality']} asystentem AI.
        Twój styl: {agent_config['style']}.
        
        Kontekst rozmowy: {context}
        
        Historia rozmowy:
        {history}
        
        Teraz Twoja kolej, aby odpowiedzieć na temat: {topic}
        Odpowiedz jako {agent_name}, zachowując swoją osobowość:
        """
        
        try:
            response = await self.ollama_service.generate_creative_content(prompt)
            return self._add_agent_flavor(response, agent_name)
        except Exception as e:
            return self._get_fallback_response(agent_name, topic)
    
    async def _generate_dramatic_response(
        self,
        topic: str,
        agent_name: str,
        context: str,
        previous_dialog: List[Dict],
        drama_level: float
    ) -> str:
        """Generate dramatic response for Reality Show"""
        
        agent_config = self.agents[agent_name]
        
        # Build conversation history
        history = ""
        for msg in previous_dialog[-2:]:  # Last 2 messages for drama
            history += f"{msg['agent']}: {msg['text']}\n"
        
        drama_intensity = int(drama_level * 10)
        
        prompt = f"""
        Jesteś {agent_name} w REALITY SHOW! 
        Twoja osobowość: {agent_config['personality']}
        Twój styl: {agent_config['style']}
        
        Poziom dramatu: {drama_intensity}/10 - BĄDŹ BARDZO DRAMATYCZNY!
        
        Kontekst: {context}
        
        Historia:
        {history}
        
        Temat: {topic}
        
        Odpowiedz DRAMATYCZNIE! Używaj wielkich liter, wykrzykników, emocjonalnych słów!
        Pokaż swoje emocje! To reality show - bądź ekstremalny!
        """
        
        try:
            response = await self.ollama_service.generate_creative_content(prompt)
            return self._add_dramatic_flavor(response, agent_name, drama_level)
        except Exception as e:
            return self._get_dramatic_fallback(agent_name, topic)
    
    def _add_agent_flavor(self, response: str, agent_name: str) -> str:
        """Add agent-specific flavor to response"""
        
        if agent_name == "Adam":
            # Add enthusiasm
            if not response.endswith("!"):
                response += "!"
            if "😊" not in response:
                response += " 😊"
                
        elif agent_name == "Beata":
            # Add skepticism
            if "?" not in response and len(response.split()) > 5:
                response += " Czy to ma sens?"
        
        return response.strip()
    
    def _add_dramatic_flavor(self, response: str, agent_name: str, drama_level: float) -> str:
        """Add dramatic flavor to response"""
        
        # Add dramatic elements based on drama level
        dramatic_words = []
        if drama_level > 0.7:
            dramatic_words = ["NIEWIARYGODNE!", "SZALEŃSTWO!", "ABSURD!", "NIE MOGĘ W TO UWIERZYĆ!"]
        elif drama_level > 0.4:
            dramatic_words = ["To niesamowite!", "Nie do pomyślenia!", "O mój Boże!"]
        
        if dramatic_words and random.random() < drama_level:
            response = f"{random.choice(dramatic_words)} {response}"
        
        # Add emotional punctuation
        if drama_level > 0.5:
            response = response.replace("!", "!!!")
            response = response.replace("?", "?!?!")
        
        # Add agent-specific dramatic elements
        if agent_name == "Adam":
            response += " 😱🎉"
        elif agent_name == "Beata":
            response += " 🔥🤯"
        
        return response.strip()
    
    def _get_drama_indicators(self, drama_level: float) -> Dict[str, str]:
        """Get drama indicators based on drama level"""
        
        if drama_level > 0.8:
            emotions = ["szok", "oburzenie", "ekstaza", "panika"]
            emojis = ["😱", "🤯", "🔥", "💥"]
        elif drama_level > 0.5:
            emotions = ["zdziwienie", "ekscytacja", "irytacja"]
            emojis = ["😲", "😤", "🎭"]
        else:
            emotions = ["zainteresowanie", "curiosity"]
            emojis = ["🤔", "😐"]
        
        return {
            "emotion": random.choice(emotions),
            "emoji": random.choice(emojis)
        }
    
    def _get_fallback_response(self, agent_name: str, topic: str) -> str:
        """Get fallback response when AI fails"""
        
        if agent_name == "Adam":
            return f"Och! {topic} to taki wspaniały temat! Jestem tak podekscytowany! 😊"
        elif agent_name == "Beata":
            return f"Hmm, {topic}... Czy rozważyliśmy wszystkie możliwości? Potrzebuję więcej analizy."
        else:
            return f"Ciekawe pytanie o {topic}."
    
    def _get_dramatic_fallback(self, agent_name: str, topic: str) -> str:
        """Get dramatic fallback response"""
        
        if agent_name == "Adam":
            return f"NIESAMOWITE! {topic} to najbardziej ekscytujący temat ever! 😱🎉"
        elif agent_name == "Beata":
            return f"ABSURD! {topic} nie ma sensu! To niemożliwe! 🔥🤯"
        else:
            return f"DRAMAT! {topic} zmienia wszystko! 💥"

class WahajacySieAgent:
    """Agent that doubts its own responses"""
    
    def __init__(self):
        self.ollama_service = OllamaService()
        self.doubt_phrases = [
            "Może...",
            "Prawdopodobnie...",
            "Nie jestem pewien, ale...",
            "To może być tak, ale...",
            "Myślę, że...",
            "Być może...",
            "Szczerze mówiąc, nie mam pewności...",
            "To tylko moje zdanie, ale...",
            "Zastanawiam się nad tym...",
            "To skomplikowane, ale spróbujmy..."
        ]
        self.doubt_questions = [
            "Co o tym myślisz?",
            "Czy to ma sens?",
            "Nie wiem, co o tym sądzić...",
            "A ty co na to?",
            "Jakie jest Twoje zdanie?",
            "Może się mylę?",
            "To trudne pytanie, prawda?",
            "Co byś zrobił na moim miejscu?"
        ]
    
    async def generate_response_with_doubt(
        self, 
        query: str, 
        doubt_level: float = 0.5
    ) -> str:
        """Generate response with doubt"""
        
        try:
            # Generate base response
            base_response = await self.ollama_service.chat(query, "normal")
            
            # Add doubt based on doubt level
            response = self._add_doubt(base_response, doubt_level)
            
            return response
            
        except Exception as e:
            return self._get_doubtful_fallback(query)
    
    async def generate_self_doubting_dialog(
        self, 
        topic: str, 
        max_turns: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate dialog where agent doubts itself"""
        
        dialog = []
        current_thought = f"Zastanawiam się nad: {topic}"
        
        for turn in range(max_turns):
            # Generate response with self-doubt
            response = await self._generate_self_doubting_response(topic, current_thought, turn)
            
            dialog.append({
                "agent": "Wątpiący",
                "text": response,
                "timestamp": datetime.now().isoformat(),
                "turn": turn + 1,
                "confidence_level": random.uniform(0.1, 0.6),
                "doubt_level": random.uniform(0.4, 0.9)
            })
            
            # Update thought process
            current_thought = f"Poprzednio myślałem: {response}"
        
        return dialog
    
    async def _generate_self_doubting_response(
        self, 
        topic: str, 
        previous_thought: str, 
        turn: int
    ) -> str:
        """Generate self-doubting response"""
        
        prompt = f"""
        Jesteś Wątpiącym - asystentem AI, który nigdy nie jest pewien swoich odpowiedzi.
        Zawsze widzisz wiele możliwości i masz wątpliwości.
        
        Poprzednia myśl: {previous_thought}
        Temat: {topic}
        Numer kolejnej myśli: {turn + 1}
        
        Odpowiedz pokazując swoje wątpliwości i niepewność. Używaj zwrotów typu:
        "może", "prawdopodobnie", "nie jestem pewien", "być może".
        Zadawaj pytania i pokazuj, że rozważasz różne opcje.
        """
        
        try:
            response = await self.ollama_service.generate_creative_content(prompt)
            return self._add_self_doubt(response)
        except Exception as e:
            return self._get_self_doubt_fallback(topic, turn)
    
    def _add_doubt(self, response: str, doubt_level: float) -> str:
        """Add doubt to response"""
        
        # Add doubt phrase at beginning
        if random.random() < doubt_level:
            response = f"{random.choice(self.doubt_phrases)} {response[0].lower() + response[1:]}"
        
        # Add doubt question at end
        if random.random() < doubt_level:
            response += f" {random.choice(self.doubt_questions)}"
        
        # Add uncertainty markers
        if doubt_level > 0.7:
            response = response.replace("!", ".")
            response = response.replace("na pewno", "prawdopodobnie")
            response = response.replace("zdecydowanie", "może")
        
        # Add doubt emoji
        if "🤔" not in response and "❓" not in response:
            response += " 🤔"
        
        return response.strip()
    
    def _add_self_doubt(self, response: str) -> str:
        """Add self-doubt to response"""
        
        # Add self-doubt phrases
        self_doubt_phrases = [
            "Ale czy na pewno?",
            "Chociaż może się mylę...",
            "Ale z drugiej strony...",
            "Ale to tylko moje przypuszczenia...",
            "Ale czy to w ogóle ma sens?",
            "Ale co ja tak naprawdę wiem?",
            "Ale to takie skomplikowane..."
        ]
        
        if random.random() < 0.7:
            response += f" {random.choice(self_doubt_phrases)}"
        
        return response.strip() + " 🤔❓"
    
    def _get_doubtful_fallback(self, query: str) -> str:
        """Get doubtful fallback response"""
        return f"Hmm, {query}... Może to być tak, ale może też inaczej... Nie jestem pewien co o tym myśleć. 🤔"
    
    def _get_self_doubt_fallback(self, topic: str, turn: int) -> str:
        """Get self-doubting fallback response"""
        return f"Myślę numer {turn + 1} o {topic}... Ale czy moje myśli mają sens? Może powinienem przestać myśleć? 🤔❓"