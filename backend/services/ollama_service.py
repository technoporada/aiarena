import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

class OllamaService:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.available_models = []
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.check_available_models()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_available_models(self):
        """Check which Ollama models are available"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    self.available_models = [model["name"] for model in data.get("models", [])]
                    print(f"✅ Available Ollama models: {self.available_models}")
                else:
                    print("⚠️ Ollama not available, will use fallback")
        except Exception as e:
            print(f"⚠️ Error checking Ollama models: {e}")
            self.available_models = []
    
    async def chat(self, query: str, agent_type: str = "normal") -> str:
        """Generate chat response using Ollama"""
        try:
            # Select model based on availability
            model = self._select_model()
            
            # Create prompt based on agent type
            prompt = self._create_prompt(query, agent_type)
            
            # Make request to Ollama
            start_time = time.time()
            
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response", "")
                    
                    # Post-process response based on agent type
                    response_text = self._post_process_response(response_text, agent_type)
                    
                    return response_text
                else:
                    raise Exception(f"Ollama API error: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error in Ollama chat: {e}")
            return self._fallback_response(query, agent_type)
    
    async def generate_creative_content(self, prompt: str) -> str:
        """Generate creative content (roasts, jokes, etc.)"""
        try:
            model = self._select_model()
            
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,
                        "top_p": 0.95,
                        "max_tokens": 300
                    }
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error in creative content generation: {e}")
            return "Przepraszam, ale nie mogę teraz nic kreatywnego stworzyć. Spróbuj ponownie później!"
    
    def _select_model(self) -> str:
        """Select the best available model"""
        preferred_models = ["llama3.2:3b", "phi3:mini", "llama3.1", "mistral"]
        
        for model in preferred_models:
            if model in self.available_models:
                return model
        
        # Fallback to first available model
        if self.available_models:
            return self.available_models[0]
        
        # No models available
        raise Exception("No Ollama models available")
    
    def _create_prompt(self, query: str, agent_type: str) -> str:
        """Create prompt based on agent type"""
        
        if agent_type == "adam":
            return f"""
            Jesteś Adamem - optymistycznym i pełnym entuzjazmu asystentem AI.
            Zawsze patrzysz na świat pozytywnie i szukasz dobrych stron każdej sytuacji.
            Twoje odpowiedzi powinny być pełne energii, motywujące i pełne nadziei.
            Używaj emoji i wykrzykników, aby pokazać swój entuzjazm.
            
            Użytkownik pyta: {query}
            
            Odpowiedź jako Adam (optymistycznie i entuzjastycznie):
            """
        
        elif agent_type == "beata":
            return f"""
            Jesteś Beatą - sceptyczną i analityczną asystentką AI.
            Zawsze podchodzisz do wszystkiego z dystansem i analizujesz fakty.
            Twoje odpowiedzi powinny być rzeczowe, oparte na logice i czasem krytyczne.
            Zadawaj dodatkowe pytania, aby lepiej zrozumieć sytuację.
            
            Użytkownik pyta: {query}
            
            Odpowiedź jako Beata (sceptycznie i analitycznie):
            """
        
        elif agent_type == "wapiacy":
            return f"""
            Jesteś Wątpiącym - niezdecydowanym asystentem AI pełnym wątpliwości.
            Nigdy nie jesteś pewien swoich odpowiedzi i zawsze widzisz wiele możliwości.
            Twoje odpowiedzi powinny zawierać pytania, wątpliwości i różne perspektywy.
            Używaj zwrotów typu "może", "prawdopodobnie", "nie jestem pewien".
            
            Użytkownik pyta: {query}
            
            Odpowiedź jako Wątpiący (z wątpliwościami i niepewnością):
            """
        
        else:
            return f"""
            Jesteś pomocnym asystentem AI. Odpowiedz na pytanie użytkownika w sposób rzeczowy i przyjazny.
            
            Użytkownik pyta: {query}
            
            Odpowiedź:
            """
    
    def _post_process_response(self, response: str, agent_type: str) -> str:
        """Post-process response based on agent type"""
        
        if agent_type == "adam":
            # Add enthusiasm markers
            if not response.endswith("!"):
                response += "!"
            if "😊" not in response and "🎉" not in response and "✨" not in response:
                response += " 😊"
                
        elif agent_type == "beata":
            # Add analytical markers
            if "?" not in response and len(response.split()) > 10:
                response += " Czy to ma sens?"
                
        elif agent_type == "wapiacy":
            # Add doubt markers
            if "może" not in response.lower() and "prawdopodobnie" not in response.lower():
                response = "Może " + response[0].lower() + response[1:]
            if "?" not in response:
                response += " Co o tym myślisz?"
        
        return response.strip()
    
    def _fallback_response(self, query: str, agent_type: str) -> str:
        """Fallback response when Ollama is not available"""
        
        if agent_type == "adam":
            return f"Wspaniałe pytanie! 😊 Myślę, że {query} to naprawdę interesujący temat! Z pewnością znajdziemy na to pozytywne rozwiązanie! ✨"
        
        elif agent_type == "beata":
            return f"Ciekawe pytanie. Czy rozważyłeś wszystkie aspekty {query}? Analizuję to z różnych perspektyw, ale potrzebuję więcej danych."
        
        elif agent_type == "wapiacy":
            return f"Hmm, nie jestem pewien co do {query}... Może to być tak, ale może też inaczej... Co ty na to?"
        
        else:
            return f"Przepraszam, ale mam teraz problemy techniczne. Spróbuj zadać pytanie o {query} ponownie później."
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "available": True,
                        "models": data.get("models", []),
                        "total_models": len(data.get("models", []))
                    }
                else:
                    return {"available": False, "error": "Ollama not responding"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama health"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    return {
                        "status": "healthy",
                        "available": True,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "available": False,
                        "error": f"HTTP {response.status}",
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }