import json
import os
from urllib import error as urlerror
from urllib import request as urlrequest
from typing import Any

from utils import call_gemini, parse_gemini_json


def call_lamini_local(prompt: str, timeout: float = 12.0) -> str:
  """Call a local Lamini-compatible endpoint and return raw text output."""
  lamini_url = os.getenv("LAMINI_LOCAL_URL", "http://127.0.0.1:8001/v1/generate")
  lamini_model = os.getenv("LAMINI_MODEL", "lamini-local")
  lamini_api_key = os.getenv("LAMINI_API_KEY", "")

  payload = {
    "model_name": lamini_model,
    "prompt": prompt,
    "max_tokens": 600,
    "temperature": 0.7,
  }
  data = json.dumps(payload).encode("utf-8")

  req = urlrequest.Request(
    lamini_url,
    data=data,
    method="POST",
    headers={
      "Content-Type": "application/json",
      **({"Authorization": f"Bearer {lamini_api_key}"} if lamini_api_key else {}),
    },
  )

  try:
    with urlrequest.urlopen(req, timeout=timeout) as resp:
      body = resp.read().decode("utf-8")
  except (urlerror.URLError, TimeoutError, ConnectionError) as exc:
    raise RuntimeError(f"Local Lamini request failed: {exc}") from exc

  if not body.strip():
    raise ValueError("Local Lamini returned an empty response.")

  try:
    parsed = json.loads(body)
  except json.JSONDecodeError:
    return body.strip()

  if isinstance(parsed, dict):
    for key in ("response", "output", "text", "generated_text"):
      val = parsed.get(key)
      if isinstance(val, str) and val.strip():
        return val.strip()
    if isinstance(parsed.get("outputs"), list) and parsed["outputs"]:
      first = parsed["outputs"][0]
      if isinstance(first, str) and first.strip():
        return first.strip()
      if isinstance(first, dict):
        for key in ("text", "output", "response"):
          val = first.get(key)
          if isinstance(val, str) and val.strip():
            return val.strip()

  if isinstance(parsed, str) and parsed.strip():
    return parsed.strip()

  raise ValueError("Could not extract text from local Lamini response.")


def explain_topic(topic: str) -> dict[str, Any]:
    prompt = f"""You are EduGenie, a friendly educational assistant for students.

Explain the following topic/concept in a beginner-friendly way.
Return ONLY valid JSON with this exact structure (no markdown fences):
{{
  "definition": "A clear one-sentence definition",
  "simple_explanation": "An easy-to-understand explanation in simple language",
  "example": "A practical example that helps understanding",
  "key_points": ["point 1", "point 2", "point 3", "point 4"]
}}

Topic: {topic}"""

    try:
      raw = call_lamini_local(prompt)
    except Exception:
      # Fallback to Gemini when local Lamini is not available or fails.
      raw = call_gemini(prompt)

    return parse_gemini_json(raw)
