import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
MODEL_NAME = os.getenv("TONY_MODEL", "gemini-2.5-pro")

# Assistant Settings
ASSISTANT_NAME = "Tony"
WAKE_WORDS = ["tony", "hey tony", "jarvis", "ultron"]
VOICE_RATE = int(os.getenv("VOICE_RATE", "175"))
VOICE_VOLUME = float(os.getenv("VOICE_VOLUME", "1.0"))

# Web Server Settings
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT") or os.getenv("SERVER_PORT", "8000"))

# Database
DB_PATH = DATA_DIR / "tony_memory.db"
