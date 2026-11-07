"""Print Hindsight relevance scores for the demo alerts, so we can choose a sensible cutoff.

Usage:  python -m scripts.probe_scores
No LLM calls are made, so this does not use your Groq token budget.
"""
from data.demo_alerts import DEMO_ALERTS
from src import memory


def main():
    c = memory.get_client()
    for name, alert in DEMO_ALERTS.items():
        print(f"\n=== {name}")
        res = c.recall(bank_id=memory.BANK_ID, query=alert, max_tokens=1500)
        for r in res.results[:8]:
            sc = r.scores
            rr = f"{sc.reranker:.3f}" if sc and sc.reranker is not None else "  n/a"
            fn = f"{sc.final:.3f}" if sc else "  n/a"
            print(f"  reranker={rr} final={fn}  {str(r.document_id or '-'):10} {r.text[:70]}")
        print(f"  ({len(res.results)} results returned in total)")


if __name__ == "__main__":
    main()
