"""Thin wrapper around Hindsight (retain / recall / reflect).

All Hindsight access in the project goes through this file, so the
memory layer is easy to point at, screenshot, and explain.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "oncall-team")
BASE_URL = os.getenv("HINDSIGHT_URL", "http://localhost:8888")

RETAIN_MISSION = (
    "You are the long-term memory of an on-call SRE team. Always keep: incident IDs, "
    "affected service, error signatures, the confirmed root cause, the fix that worked, "
    "and fixes that FAILED (state clearly that they failed). Keep engineer corrections "
    "and durable environment facts (deploy schedules, shared infrastructure). "
    "Ignore greetings and chatter."
)
REFLECT_MISSION = (
    "You are a senior SRE who has worked on this system for years. Spot recurring "
    "failure patterns across incidents, say which fixes worked and which did not, and "
    "be direct. Prefer evidence from past incidents over generic advice. If the memory "
    "does not support a claim, say so."
)


@dataclass
class Memory:
    id: str
    text: str
    kind: str = ""


def get_client() -> Hindsight:
    return Hindsight(base_url=BASE_URL)


def setup_bank(client=None) -> str:
    """Create the bank and give it an SRE-specific mission. Returns a status string."""
    c = client or get_client()
    try:
        c.create_bank(bank_id=BANK_ID)
    except Exception:
        pass  # bank already exists, which is fine
    try:
        c.update_bank_config(
            BANK_ID,
            retain_mission=RETAIN_MISSION,
            reflect_mission=REFLECT_MISSION,
            disposition_skepticism=4,   # doubt old fixes that may no longer apply
            disposition_literalism=3,
            disposition_empathy=1,      # facts over feelings during an outage
        )
        return "configured"
    except Exception as e:  # older server versions may lack this endpoint
        return f"bank ready, config skipped ({e})"


def retain(content: str, context: str, tags=None, document_id=None, client=None) -> None:
    """Store a memory. A stable document_id makes re-seeding idempotent."""
    c = client or get_client()
    c.retain(bank_id=BANK_ID, content=content, context=context,
             tags=tags or [], document_id=document_id)


def recall(query: str, max_tokens: int = 2048, client=None) -> list:
    c = client or get_client()
    res = c.recall(bank_id=BANK_ID, query=query, max_tokens=max_tokens)
    out = []
    for r in res.results:
        out.append(Memory(id=str(getattr(r, "id", "")), text=r.text,
                          kind=str(getattr(r, "type", "") or "")))
    return out


def reflect(query: str, client=None):
    """Cross-incident reasoning. Returns (text, supporting memories)."""
    c = client or get_client()
    r = c.reflect(bank_id=BANK_ID, query=query, include_facts=True)
    facts = []
    if getattr(r, "based_on", None) and getattr(r.based_on, "memories", None):
        facts = [Memory(id=str(getattr(m, "id", "")), text=m.text) for m in r.based_on.memories]
    return r.text, facts
