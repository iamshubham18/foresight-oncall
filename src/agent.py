"""The incident copilot: alert in, answer out, with or without memory."""
import time
from dataclasses import dataclass, field
from datetime import date

from src import memory
from src.llm import chat

SYSTEM = """You are Foresight, an on-call incident copilot for an SRE team.

Answer in exactly this format, short and concrete:
**Matching history:** incident IDs that truly match this alert, or "None found".
**Likely cause:** one or two sentences.
**Check first:** up to 3 ordered steps.
**Do not waste time on:** fixes that FAILED in a matching incident (omit if none known).
**Confidence:** low / medium / high, with one clause of reasoning.

Rules for using MEMORY:
- MEMORY is grouped under headers such as [INC-0388]. Facts under a header belong ONLY to that
  incident. Never attribute a fact to a different incident.
- MEMORY holds the nearest matches by similarity and may be unrelated. An incident matches only
  if it shares the same failure mode and symptoms as the alert, not just the same technology.
- If no incident matches, write "None found", say plainly that the team has no history of this
  failure, and give only generic checks labelled as generic. Do not present lessons from
  unrelated incidents as evidence.
- A [learned-pattern] group is a summary Hindsight built itself from several incidents. It has no
  incident ID. Use it as supporting evidence, but never cite it as an incident.
- Cite incident IDs for every claim taken from memory. Never invent incidents.
- Never claim certainty you do not have."""


def format_memories(memories) -> str:
    """Group recalled facts by source incident so the model cannot blur incidents together."""
    groups: dict = {}
    for m in memories:
        groups.setdefault(m.source, []).append(m.text)
    return "\n\n".join(f"[{doc}]\n" + "\n".join(f"- {t}" for t in texts)
                        for doc, texts in groups.items())


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
        block = format_memories(memories) or "(no relevant memories)"
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
