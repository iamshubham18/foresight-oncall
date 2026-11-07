"""Load the synthetic incident history into Hindsight.

Usage:  python -m scripts.seed
Each retain triggers LLM fact extraction, so expect a few seconds per incident.
"""
import time

from data.incidents import ENV_FACTS, INCIDENTS, incident_to_text
from src import memory


def main():
    c = memory.get_client()
    print("Bank setup:", memory.setup_bank(c))
    for i in INCIDENTS:
        t = time.time()
        memory.retain(incident_to_text(i), context=f"Post-mortem {i['id']}",
                      tags=[f"service:{i['service']}", f"sev:{i['sev']}", "source:postmortem"],
                      document_id=i["id"], client=c)
        print(f"retained {i['id']} ({time.time() - t:.1f}s)")
    for f in ENV_FACTS:
        memory.retain(f, context="Environment knowledge", tags=["source:env"],
                      document_id=f"env-{ENV_FACTS.index(f)}", client=c)
        print("retained env fact")
    print("Done. Open http://localhost:9999 to browse the memory bank.")


if __name__ == "__main__":
    main()
