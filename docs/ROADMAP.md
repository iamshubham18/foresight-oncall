# Roadmap

Status key: ✅ done · 🔄 in progress · ⬜ planned. Dates are relative; adjust to the real deadline.

## Phase 0: Foundation ✅
- ✅ Repo scaffold, Groq wrapper with retry and fallback
- ✅ Hindsight memory wrapper (bank mission, retain, recall, reflect)
- ✅ 11 synthetic incidents and 3 environment facts
- ✅ Streamlit UI: memory toggle, memory panel, feedback form
- ✅ Seed and smoke-test scripts, UI render test (mocked)

## Phase 1: Verify against real services 🔄
- ⬜ Start Hindsight (Docker, Groq as server LLM) and run `scripts.smoke_test`
- ⬜ Seed the bank and inspect memories in the Hindsight UI (`localhost:9999`)
- ⬜ Run the test plan (`docs/TEST_PLAN.md`), log results
- ⬜ Fix whatever breaks (expect recall-quality and latency tuning)

## Phase 2: Make memory the star ⬜
- ⬜ Tune recall: query phrasing, `budget`, tag filters per service
- ⬜ Show source incident ID and date on each memory in the panel
- ⬜ **Contradiction handling:** when feedback says a past fix failed, mark it stale and surface that
- ⬜ Memory ON vs OFF side-by-side view for the same alert
- ⬜ Evaluate Hindsight mental models for a per-service "what we know" summary

## Phase 3: Demo polish ⬜
- ⬜ Rehearse the 3-minute script (`docs/DEMO_SCRIPT.md`)
- ⬜ Record a backup run in case of live failure
- ⬜ Screenshots: memory panel, Hindsight UI, before/after
- ⬜ Architecture diagram image for the article

## Phase 4: Content and submission ⬜
- ⬜ README final pass, repo clean-up
- ⬜ Article, LinkedIn post, Reddit post, video and thumbnail (see `_internal/SUBMISSION_CHECKLIST.md`)

## Later (beyond the competition)
- Alert intake from PagerDuty / Alertmanager webhooks
- Slack bot: post the recommendation in the incident channel
- Auto-draft post-mortem and retain it
- Multi-agent split (triage, historian, responder, scribe), possibly coordinated through Band AI
- Per-team banks and access control
