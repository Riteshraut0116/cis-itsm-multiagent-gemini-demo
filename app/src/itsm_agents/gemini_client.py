from google import genai
from google.genai import types

from .config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS
from .json_utils import load_json_strict

class GeminiClient:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY missing in .env")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        prompt = (
            f"{system_prompt}\n\n"
            "STRICT RULES:\n"
            "1) Output ONLY JSON\n"
            "2) No markdown, no ```\n"
            "3) No trailing commas\n\n"
            f"{user_prompt}"
        )

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            ),
        )

        text = (resp.text or "").strip()
        return load_json_strict(text)