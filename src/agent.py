"""The incident copilot: alert in, answer out, with or without memory."""
import time
from dataclasses import dataclass, field
from datetime import date

from src import memory
from src.llm import chat

SYSTEM = """You are Foresight, an on-call incident copilot for an SRE team.

Answer in exactly this format, short and concrete:
**Likely cause:** one or two sentences.
**Check first:** up to 3 ordered steps.
**Do not waste time on:** things known to fail (only if known, else omit this line).
**Confidence:** low / medium / high, with one clause of reasoning.

Rules:
- If MEMORY is provided, ground your answer in it and cite incident IDs like INC-0388.
- Explicitly say what was tried before and FAILED, so the engineer skips it.
- If memory is empty or unrelated, say you have no matching history. Never invent past incidents.
- Never claim certainty you do not have."""


@dataclass
class Result:
    answer: str
    memories: list = field(default_factory=list)
    pattern: str = ""
    used_memory: bool = False
    seconds: float = 0.0


def analyze(alert: str, use_memory: bool = True, deep: bool = False) -> Result:
    t0 = time.time()
    memories, pattern = [], ""
    user = f"ALERT:\n{alert}"

    if use_memory:
        try:
            memories = memory.recall(alert)
            if deep:
                pattern, _ = memory.reflect(
                    "Given this alert, what past incidents are relevant, what was the root "
                    "cause and fix each time, and what failed?\n\n" + alert)
        except Exception as e:
            pattern = f"(memory unavailable: {e})"
        block = "\n".join(f"- {m.text}" for m in memories) or "(no relevant memories)"
        user += f"\n\nMEMORY (recalled from past incidents):\n{block}"
        if pattern:
            user += f"\n\nPATTERN ANALYSIS (from reflect):\n{pattern}"

    answer = chat([{"role": "system", "content": SYSTEM},
                   {"role": "user", "content": user}])
    return Result(answer=answer, memories=memories, pattern=pattern,
                  used_memory=use_memory, seconds=time.time() - t0)


def build_feedback_text(alert, suggestion, outcome, root_cause, notes, inc) -> str:
    return (
        f"Incident {inc} on {date.today().isoformat()}. Alert: {alert.strip()}\n"
        f"The copilot suggested: {suggestion.strip()[:600]}\n"
        f"Engineer verdict on the suggestion: {outcome}.\n"
        f"Confirmed root cause: {root_cause.strip() or 'not stated'}.\n"
        f"Engineer notes (what fixed it, what failed): {notes.strip() or 'none'}."
    )


def retain_feedback(alert, suggestion, outcome, root_cause, notes, incident_no: int) -> str:
    """Write the engineer's correction back into memory. This is the learning loop."""
    inc = f"INC-L{incident_no:03d}"
    content = build_feedback_text(alert, suggestion, outcome, root_cause, notes, inc)
    memory.retain(content, context=f"Live incident feedback {inc}",
                  tags=["source:feedback", f"incident:{inc}"], document_id=inc)
    return inc
