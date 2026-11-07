# Foresight (foresight-oncall)

> The on-call copilot that remembers every outage. Hindsight gives it memory; that memory gives you foresight.

An incident-response agent built on **Hindsight** (long-term memory) and **Groq** (LLM).
Paste an alert and it recalls similar past incidents, what fixed them, and what *failed*.
After the incident, the engineer's correction is retained, so the next answer is better.

## How Hindsight is used
| Operation | Where | Purpose |
|---|---|---|
| `create_bank` / `update_bank_config` | `src/memory.py: setup_bank` | SRE-specific retain and reflect missions, skeptical disposition |
| `retain` | `scripts/seed.py`, `src/agent.py: retain_feedback` | Post-mortems, environment facts, live engineer corrections |
| `recall` | `src/agent.py: analyze` | Pull similar past incidents for every new alert |
| `reflect` | `src/agent.py: analyze (deep)` | Reason across incidents to find recurring patterns |

The UI has a **Memory ON/OFF toggle** and a **Memory panel** showing exactly what was recalled.

## Setup
1. Start Hindsight (open source, Docker). Check https://hindsight.vectorize.io/developer/installation for the current flags.
   ```bash
   docker run --rm -it --pull always -p 8888:8888 -p 9999:9999 \
     -e HINDSIGHT_API_LLM_PROVIDER=groq \
     -e HINDSIGHT_API_LLM_API_KEY=$GROQ_API_KEY \
     -e HINDSIGHT_API_LLM_MODEL=openai/gpt-oss-120b \
     -v $HOME/.hindsight-docker:/home/hindsight/.pg0 \
     ghcr.io/vectorize-io/hindsight:latest
   ```
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and add your `GROQ_API_KEY`
4. `python -m scripts.smoke_test`   (checks Hindsight + Groq)
5. `python -m scripts.seed`         (loads 11 incidents and 3 environment facts)
6. `streamlit run app.py`

## Demo script (3 min)
1. Toggle memory **OFF**, load demo alert 1: generic advice.
2. Toggle memory **ON**, same alert: cites INC-0388 and INC-0412, lists failed fixes.
3. Load alert 4 (unseen): the agent says it has no matching history.
4. Submit feedback with a real correction, re-run the alert, and show the answer change.

## Documentation
- [Product requirements](docs/PRD.md)
- [Roadmap](docs/ROADMAP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [How Hindsight memory is used](docs/HINDSIGHT_USAGE.md)
- [Test plan](docs/TEST_PLAN.md)
- [Demo script](docs/DEMO_SCRIPT.md)
