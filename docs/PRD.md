# Product Requirements: Foresight

**Status:** MVP in build  ·  **Owner:** solo  ·  **Last updated:** 2026-11-07

## 1. Problem
On-call engineers re-learn the same outages. The root cause of last month's incident lives in a
post-mortem nobody reads at 2 a.m., or in the head of someone who left. During an outage every
minute costs money, and the most expensive minutes are spent trying fixes the team already knows fail.

## 2. Who it is for
**Primary: the on-call SRE / platform engineer.** Paged at night, unfamiliar with part of the stack,
needs "what is this, what do I check first, what should I NOT waste time on."
**Secondary: the engineering manager**, who wants post-incident learning to compound instead of evaporate.

## 3. Product idea
Paste an alert. The agent recalls similar past incidents from long-term memory (Hindsight) and
answers with the likely cause, the first checks, and the fixes that already **failed**. After the
incident, the engineer's correction is saved, so the next answer is better.

## 4. Goals
1. Answer an alert in under ~15 seconds with history-grounded guidance.
2. Make memory **visible**: show exactly which past incidents informed the answer.
3. Learn from engineer feedback with no retraining.
4. Be honest: say "no matching history" instead of inventing one.

## 5. Non-goals (MVP)
- No live integrations (PagerDuty, Datadog, Slack). Alerts are pasted.
- No automated remediation. The agent advises; a human acts.
- No multi-tenant auth or permissions.
- Not a replacement for runbooks or monitoring.

## 6. User stories
| ID | As an on-call engineer I want to... | So that... |
|---|---|---|
| US1 | paste an alert and get a likely cause | I start from a hypothesis, not a blank page |
| US2 | see which past incidents were recalled | I can judge whether to trust the answer |
| US3 | be told which fixes already failed | I skip dead ends |
| US4 | record what actually fixed it | the next engineer benefits |
| US5 | be told when there is no matching history | I do not chase a fabricated lead |
| US6 | compare the answer with memory off | I (and judges) can see memory's value |

## 7. Functional requirements
| ID | Requirement | Priority |
|---|---|---|
| FR1 | Accept free-text alert or log excerpt | Must |
| FR2 | Recall relevant memories from Hindsight for each alert | Must |
| FR3 | Produce structured answer: cause, checks, avoid, confidence | Must |
| FR4 | Memory panel lists recalled memories | Must |
| FR5 | Memory ON/OFF toggle for before/after comparison | Must |
| FR6 | Feedback form retains verdict, root cause, notes to Hindsight | Must |
| FR7 | Optional deep analysis via Hindsight `reflect` | Should |
| FR8 | Seed script loads synthetic incident history idempotently | Must |
| FR9 | Graceful degradation if Hindsight or Groq is unreachable | Should |
| FR10 | Flag a past fix as stale when new feedback contradicts it | Could (Phase 2) |

## 8. Non-functional requirements
- **Latency:** recall + answer target < 15 s (reflect adds more).
- **Reliability:** Groq retried, with a fallback model; no tool-calling dependency.
- **Honesty:** the system prompt forbids inventing past incidents.
- **Privacy:** no secrets retained. Feedback text is user-supplied, so the UI warns against pasting credentials (Phase 2).
- **Portability:** runs locally with Docker + Python; no cloud account required.

## 9. Success metrics (targets, measured via `docs/TEST_PLAN.md`)
| Metric | Target |
|---|---|
| Memory-ON answers cite the correct past incident for seeded families | >= 3 of 3 demo alerts |
| Memory-ON answers list at least one known failed fix where one exists | >= 3 of 3 |
| Unseen alert yields "no matching history" rather than a fabricated incident | 1 of 1 |
| After feedback, a re-run of the same alert reflects the correction | observed in demo |

These are targets to verify, not results already achieved.

## 10. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Recall returns loosely related memories | Tune query, tags, and `budget`; show memories so the human can judge |
| LLM over-trusts a stale fix | Skeptical bank disposition; Phase 2 contradiction handling |
| Synthetic data looks fake | Realistic error strings, dates, services, and failed-fix details |
| Groq rate limits during demo | Retry, fallback model, pre-recorded backup run |
| Hindsight server down during demo | Smoke test before demo; app shows a clear error |

## 11. Open questions
- Best recall budget (`low`/`mid`/`high`) for latency vs. quality?
- Should feedback be tagged per service to scope recall?
- Does `reflect` justify its latency in the live demo, or only in the video?
