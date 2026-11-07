"""Quick end-to-end check: Hindsight reachable, retain works, recall finds it, Groq answers."""
from src import memory
from src.llm import chat


def main():
    print("1/3 Hindsight bank:", memory.setup_bank())
    memory.retain("Incident INC-TEST: smoke test. Root cause was a typo in the config.",
                  context="smoke test", tags=["source:test"])
    hits = memory.recall("What was the root cause of the smoke test incident?")
    print(f"2/3 recall returned {len(hits)} memories")
    for h in hits[:3]:
        print("   -", h.text[:100])
    print("3/3 Groq says:", chat([{"role": "user", "content": "Reply with the single word: ready"}], max_tokens=300))


if __name__ == "__main__":
    main()
