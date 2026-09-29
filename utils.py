import json
import re
from functools import lru_cache
from typing import Any

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, require_api_key


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    require_api_key()
    return genai.Client(api_key=GEMINI_API_KEY)


def clean_json_response(text: str) -> str:
    """Strip markdown code fences from model output."""
    text = text.strip()
    fence_match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```$", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text


def parse_gemini_json(text: str) -> Any:
    cleaned = clean_json_response(text)
    return json.loads(cleaned)


def call_gemini(prompt: str, temperature: float = 0.7) -> str:
    client = get_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )
    if not response.text:
        raise ValueError("Gemini returned an empty response.")
    return response.text.strip()
