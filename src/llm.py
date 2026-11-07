"""Groq chat wrapper with retry and model fallback.

We deliberately avoid Groq tool/function calling: Hindsight already supplies
structured memory, and plain chat completions cannot fail with malformed
tool-call JSON, which the organisers warned about.
"""
import os
import re
import time

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODELS = [
    os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    os.getenv("GROQ_FALLBACK_MODEL", "qwen/qwen3-32b"),
]


def chat(messages, temperature: float = 0.2, max_tokens: int = 1500) -> str:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    last_error = None
    for model in MODELS:
        for attempt in range(2):
            try:
                r = client.chat.completions.create(
                    model=model, messages=messages,
                    temperature=temperature, max_tokens=max_tokens,
                )
                text = r.choices[0].message.content or ""
                return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            except Exception as e:  # rate limit, 5xx, model hiccup
                last_error = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"All Groq models failed: {last_error}")
