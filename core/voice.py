import pyttsx3
import speech_recognition as sr
import threading
import queue
import time
from typing import Callable, Optional
from config import VOICE_RATE, VOICE_VOLUME

class VoiceEngine:
    """Robust dual-channel Voice I/O (STT and TTS) for Tony AI."""

    def __init__(self, on_speech_start: Optional[Callable] = None, on_speech_end: Optional[Callable] = None):
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        
        # Initialize pyttsx3 engine
        self.engine = None
        self._init_tts()
        
        # Audio playback queue
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self._start_speech_worker()

        # Speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.is_listening = False

    def _init_tts(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", VOICE_RATE)
            self.engine.setProperty("volume", VOICE_VOLUME)
            voices = self.engine.getProperty("voices")
            for v in voices:
                if "david" in v.name.lower() or "mark" in v.name.lower() or "male" in v.name.lower():
                    self.engine.setProperty("voice", v.id)
                    break
        except Exception as e:
            # Headless Linux / cloud environment without sound drivers
            self.engine = None

    def _start_speech_worker(self):
        def worker():
            while True:
                text = self.speech_queue.get()
                if text is None:
                    break
                self.is_speaking = True
                if self.on_speech_start:
                    self.on_speech_start(text)
                try:
                    if self.engine:
                        eng = pyttsx3.init()
                        eng.setProperty("rate", VOICE_RATE)
                        eng.setProperty("volume", VOICE_VOLUME)
                        eng.say(text)
                        eng.runAndWait()
                except Exception:
                    pass
                finally:
                    self.is_speaking = False
                    if self.on_speech_end:
                        self.on_speech_end()
                    self.speech_queue.task_done()

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def speak(self, text: str, block: bool = False):
        """Speaks the text output."""
        clean_text = text.replace("*", "").replace("#", "").replace("`", "")
        self.speech_queue.put(clean_text)
        if block:
            self.speech_queue.join()

    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """Listens to microphone for a single phrase and returns transcribed string."""
        self.is_listening = True
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # Use Google Speech Recognition API
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[VoiceEngine Listen Error]: {e}")
            return ""
        finally:
            self.is_listening = False
