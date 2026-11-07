"""Groq chat wrapper with retry, rate-limit waiting, and optional fallback model.

We deliberately avoid Groq tool/function calling: Hindsight already supplies
structured memory, and plain chat completions cannot fail with malformed
tool-call JSON.
"""
import os
import re
import time

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _models() -> list:
    primary = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
    fallback = os.getenv("GROQ_FALLBACK_MODEL", "").strip()  # empty = no fallback
    return [m for m in (primary, fallback) if m]


def _is_rate_limit(e: Exception) -> bool:
    s = str(e).lower()
    return "429" in s or "rate limit" in s or "rate_limit" in s


def _is_missing_model(e: Exception) -> bool:
    s = str(e).lower()
    return "404" in s or "model_not_found" in s


def chat(messages, temperature: float = 0.2, max_tokens: int = 1500) -> str:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    errors = []
    for model in _models():
        for attempt in range(3):
            try:
                r = client.chat.completions.create(
                    model=model, messages=messages,
                    temperature=temperature, max_tokens=max_tokens,
                )
                text = r.choices[0].message.content or ""
                return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            except Exception as e:
                errors.append(f"[{model}] {str(e)[:200]}")
                if _is_missing_model(e):
                    break  # retrying a model that does not exist is pointless
                # Groq's free tier limits tokens per minute: wait for the window to reset
                time.sleep(15 if _is_rate_limit(e) else 2 * (attempt + 1))
    raise RuntimeError("All Groq models failed. " + " | ".join(errors[-3:]))