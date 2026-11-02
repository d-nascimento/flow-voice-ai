import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do .env na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
HOTKEY_PUSH_TO_TALK = os.getenv("HOTKEY_PUSH_TO_TALK", "ctrl+space")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "pt")
ENABLE_CONTEXT_AWARENESS = os.getenv("ENABLE_CONTEXT_AWARENESS", "true").lower() == "true"
SAMPLE_RATE = 16000  # 16kHz é o padrão otimizado para o Whisper
CHANNELS = 1         # Mono
