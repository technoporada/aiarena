import asyncio
import io
import tempfile
import os
from typing import Dict, Any, Optional
import pyttsx3
from gtts import gTTS
import pygame
import threading
import time

class TTSService:
    """Text-to-Speech service with multiple engines and voices"""
    
    def __init__(self):
        self.pyttsx3_engine = None
        self.gtts_available = True
        self.audio_cache = {}
        self.currently_playing = False
        
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        if self.pyttsx3_engine is None:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                # Get available voices
                voices = self.pyttsx3_engine.getProperty('voices')
                print(f"✅ Available pyttsx3 voices: {len(voices)}")
                return True
            except Exception as e:
                print(f"❌ Failed to initialize pyttsx3: {e}")
                return False
        return True
    
    async def generate_speech(
        self,
        text: str,
        voice_config: Dict[str, Any],
        speed: float = 1.0,
        pitch: float = 1.0,
        emotion: str = "neutral"
    ) -> bytes:
        """Generate speech audio data"""
        
        engine = voice_config.get("engine", "pyttsx3")
        
        if engine == "pyttsx3":
            return await self._generate_pyttsx3_speech(text, voice_config, speed, pitch, emotion)
        elif engine == "gtts":
            return await self._generate_gtts_speech(text, voice_config, speed)
        else:
            raise ValueError(f"Unsupported TTS engine: {engine}")
    
    async def _generate_pyttsx3_speech(
        self,
        text: str,
        voice_config: Dict[str, Any],
        speed: float,
        pitch: float,
        emotion: str
    ) -> bytes:
        """Generate speech using pyttsx3"""
        
        if not self._init_pyttsx3():
            raise Exception("pyttsx3 not available")
        
        # Create cache key
        cache_key = f"pyttsx3_{hash(text)}_{speed}_{pitch}_{emotion}"
        
        if cache_key in self.audio_cache:
            return self.audio_cache[cache_key]
        
        # Configure engine
        engine = self.pyttsx3_engine
        
        # Set voice properties
        properties = voice_config.get("properties", {})
        
        # Set rate (speed)
        base_rate = properties.get("rate", 150)
        engine.setProperty('rate', int(base_rate * speed))
        
        # Set volume
        volume = properties.get("volume", 0.9)
        engine.setProperty('volume', volume)
        
        # Set voice
        voice_id = properties.get("voice_id")
        if voice_id:
            engine.setProperty('voice', voice_id)
        
        # Apply emotion modifications
        if emotion != "neutral":
            text = self._apply_emotion_to_text(text, emotion)
        
        # Generate audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            # Save to file
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            # Read the file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Cache the result
            self.audio_cache[cache_key] = audio_data
            
            return audio_data
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    async def _generate_gtts_speech(
        self,
        text: str,
        voice_config: Dict[str, Any],
        speed: float
    ) -> bytes:
        """Generate speech using gTTS"""
        
        if not self.gtts_available:
            raise Exception("gTTS not available")
        
        # Create cache key
        cache_key = f"gtts_{hash(text)}_{speed}"
        
        if cache_key in self.audio_cache:
            return self.audio_cache[cache_key]
        
        try:
            # Get language
            properties = voice_config.get("properties", {})
            lang = properties.get("lang", "pl")
            
            # Apply emotion modifications
            emotion = "neutral"  # gTTS doesn't support emotion well
            text = self._apply_emotion_to_text(text, emotion)
            
            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_data = audio_buffer.getvalue()
            
            # Cache the result
            self.audio_cache[cache_key] = audio_data
            
            return audio_data
            
        except Exception as e:
            print(f"❌ gTTS error: {e}")
            raise Exception(f"gTTS generation failed: {e}")
    
    def _apply_emotion_to_text(self, text: str, emotion: str) -> str:
        """Apply emotion modifications to text"""
        
        emotion_modifiers = {
            "happy": {
                "prefix": ["Oh! ", "Wow! ", "Great! "],
                "suffix": ["! 😊", "! 🎉", "! ✨"],
                "replacements": {
                    "jest": "jest naprawdę",
                    "mam": "mam super",
                    "może": "na pewno"
                }
            },
            "sad": {
                "prefix": ["Oh... ", "Hmm... ", "Well... "],
                "suffix": ["... 😔", "... 😢", "... 💔"],
                "replacements": {
                    "jest": "jest niestety",
                    "mam": "mam tylko",
                    "może": "chyba nie"
                }
            },
            "angry": {
                "prefix": ["What! ", "Hey! ", "Listen! "],
                "suffix": ["! 😤", "! 🔥", "! 💢"],
                "replacements": {
                    "jest": "jest po prostu",
                    "mam": "mam dość",
                    "może": "absolutnie nie"
                }
            },
            "surprised": {
                "prefix": ["Wow! ", "Oh my! ", "Really! "],
                "suffix": ["! 😲", "! 😱", "! 🤯"],
                "replacements": {
                    "jest": "jest niesamowicie",
                    "mam": "mam nagle",
                    "może": "naprawdę"
                }
            },
            "doubtful": {
                "prefix": ["Well... ", "Hmm... ", "Maybe... "],
                "suffix": ["... 🤔", "... ❓", "... 🤷"],
                "replacements": {
                    "jest": "może jest",
                    "mam": "chyba mam",
                    "może": "raczej może"
                }
            },
            "excited": {
                "prefix": ["OMG! ", "Wow! ", "Amazing! "],
                "suffix": ["! 🎉", "! ✨", "! 🚀"],
                "replacements": {
                    "jest": "jest absolutnie",
                    "mam": "mam fantastycznie",
                    "może": "zdecydowanie"
                }
            }
        }
        
        if emotion not in emotion_modifiers:
            return text
        
        modifier = emotion_modifiers[emotion]
        
        # Apply prefix
        if modifier["prefix"] and len(text.split()) > 3:
            text = f"{random.choice(modifier['prefix'])}{text[0].lower() + text[1:]}"
        
        # Apply replacements
        for old_word, new_word in modifier["replacements"].items():
            text = text.replace(old_word, new_word)
        
        # Apply suffix
        if modifier["suffix"]:
            text += random.choice(modifier["suffix"])
        
        return text
    
    async def play_audio(self, audio_data: bytes):
        """Play audio data"""
        
        def _play_audio_thread():
            try:
                # Initialize pygame mixer
                pygame.mixer.init()
                
                # Load and play audio
                audio_buffer = io.BytesIO(audio_data)
                pygame.mixer.music.load(audio_buffer)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.quit()
                
            except Exception as e:
                print(f"❌ Audio playback error: {e}")
        
        # Play in separate thread to avoid blocking
        if not self.currently_playing:
            self.currently_playing = True
            thread = threading.Thread(target=_play_audio_thread)
            thread.daemon = True
            thread.start()
            
            # Wait for thread to finish
            thread.join()
            self.currently_playing = False
    
    async def speak_text(
        self,
        text: str,
        voice_config: Dict[str, Any],
        speed: float = 1.0,
        pitch: float = 1.0,
        emotion: str = "neutral"
    ):
        """Generate and speak text"""
        
        try:
            # Generate audio
            audio_data = await self.generate_speech(
                text, voice_config, speed, pitch, emotion
            )
            
            # Play audio
            await self.play_audio(audio_data)
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
    
    async def clear_cache(self) -> bool:
        """Clear audio cache"""
        try:
            self.audio_cache.clear()
            return True
        except Exception as e:
            print(f"❌ Cache clear error: {e}")
            return False
    
    def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        
        voice_configs = {
            "adam": {
                "name": "Adam (Optymista)",
                "engine": "pyttsx3",
                "gender": "male",
                "language": "pl-PL",
                "description": "Optymistyczny, pełen entuzjazmu głos",
                "emotions_supported": ["happy", "excited", "surprised", "neutral"]
            },
            "beata": {
                "name": "Beata (Sceptyczna)",
                "engine": "pyttsx3", 
                "gender": "female",
                "language": "pl-PL",
                "description": "Sceptyczny, analityczny głos",
                "emotions_supported": ["sad", "angry", "doubtful", "neutral"]
            },
            "wapiacy": {
                "name": "Wątpiący",
                "engine": "pyttsx3",
                "gender": "male", 
                "language": "pl-PL",
                "description": "Niezdecydowany, pełen wątpliwości głos",
                "emotions_supported": ["doubtful", "sad", "surprised", "neutral"]
            },
            "gtts_adam": {
                "name": "Adam (GTTS)",
                "engine": "gtts",
                "gender": "male",
                "language": "pl",
                "description": "Adam głos z Google TTS",
                "emotions_supported": ["neutral"]
            },
            "gtts_beata": {
                "name": "Beata (GTTS)",
                "engine": "gtts",
                "gender": "female",
                "language": "pl", 
                "description": "Beata głos z Google TTS",
                "emotions_supported": ["neutral"]
            }
        }
        
        return voice_configs.get(voice_id, {})
    
    async def test_voice(self, voice_id: str, test_text: str = None) -> bool:
        """Test a specific voice"""
        
        if test_text is None:
            test_text = "Cześć! To jest test mojego głosu. Jak brzmię?"
        
        try:
            voice_config = self.get_voice_info(voice_id)
            if not voice_config:
                return False
            
            # Generate test audio
            audio_data = await self.generate_speech(
                test_text, voice_config, 1.0, 1.0, "neutral"
            )
            
            # Play test audio
            await self.play_audio(audio_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Voice test error: {e}")
            return False
    
    async def batch_generate(
        self,
        texts: list[str],
        voice_config: Dict[str, Any],
        speed: float = 1.0,
        pitch: float = 1.0,
        emotion: str = "neutral"
    ) -> list[bytes]:
        """Generate multiple speech files"""
        
        tasks = []
        for text in texts:
            task = self.generate_speech(text, voice_config, speed, pitch, emotion)
            tasks.append(task)
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        audio_files = []
        for result in results:
            if isinstance(result, Exception):
                print(f"❌ Batch generation error: {result}")
            else:
                audio_files.append(result)
        
        return audio_files