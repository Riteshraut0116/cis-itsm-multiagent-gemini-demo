import os
from dotenv import load_dotenv

load_dotenv()

def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

GEMINI_API_KEY = env("GEMINI_API_KEY")
GEMINI_MODEL = env("GEMINI_MODEL", "gemini-2.5-flash")

TEMPERATURE = float(env("TEMPERATURE", "0.2"))
MAX_OUTPUT_TOKENS = int(env("MAX_OUTPUT_TOKENS", "1200"))