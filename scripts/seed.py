"""Load the synthetic incident history into Hindsight, throttled for Groq's free tier.

Usage:  python -m scripts.seed
Safe to re-run: finished items are remembered in .seed_done.json.
"""
import json
import os
import time

from data.incidents import ENV_FACTS, INCIDENTS, incident_to_text
from src import memory

STATE = ".seed_done.json"
PAUSE = int(os.getenv("SEED_PAUSE_SECONDS", "50"))  # gap between items
RETRIES = 4
RATE_WORDS = ("429", "rate limit", "quota", "tokens per minute")


def load_done() -> set:
    try:
        with open(STATE) as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_done(done: set) -> None:
    with open(STATE, "w") as f:
        json.dump(sorted(done), f)


def retain_with_retry(label: str, **kwargs) -> bool:
    for attempt in range(1, RETRIES + 1):
        try:
            memory.retain(**kwargs)
            return True
        except Exception as e:
            if any(w in str(e).lower() for w in RATE_WORDS):
                print(f"  rate limited on {label}; waiting 70s (attempt {attempt}/{RETRIES})")
                time.sleep(70)
                continue
            raise
    return False


def main():
    c = memory.get_client()
    print("Bank setup:", memory.setup_bank(c))
    done = load_done()

    work = [(i["id"], dict(
                content=incident_to_text(i), context=f"Post-mortem {i['id']}",
                tags=[f"service:{i['service']}", f"sev:{i['sev']}", "source:postmortem"],
                document_id=i["id"], client=c)) for i in INCIDENTS]
    work += [(f"env-{n}", dict(
                content=f, context="Environment knowledge", tags=["source:env"],
                document_id=f"env-{n}", client=c)) for n, f in enumerate(ENV_FACTS)]

    todo = [w for w in work if w[0] not in done]
    print(f"{len(todo)} of {len(work)} items to load (about {len(todo)} minutes).")
    for n, (label, kwargs) in enumerate(todo, 1):
        t = time.time()
        if not retain_with_retry(label, **kwargs):
            print(f"Giving up on {label}. Re-run the script to continue.")
            return
        done.add(label)
        save_done(done)
        print(f"[{n}/{len(todo)}] retained {label} ({time.time() - t:.1f}s)")
        if n < len(todo):
            time.sleep(PAUSE)
    print("Done. Open http://localhost:9999 to browse the memory bank.")


if __name__ == "__main__":
    main()