# Test Plan

Run these in order. Record results in the log at the bottom.

## A. Environment checks
| # | Step | Expected |
|---|---|---|
| A1 | Hindsight container starts; `http://localhost:9999` loads | UI visible |
| A2 | `python -m scripts.smoke_test` | Bank configured, recall returns >= 1 memory, Groq replies "ready" |
| A3 | `python -m scripts.seed` | 11 incidents + 3 env facts retained, no exceptions |
| A4 | Hindsight UI shows the `oncall-team` bank with memories | Facts and entities visible |
| A5 | Re-run seed | No duplicate documents (same `document_id`) |

## B. Functional tests (app)
| # | Action | Expected |
|---|---|---|
| B1 | Load demo alert 1, memory ON, Analyze | Structured answer; memory panel populated |
| B2 | Same alert, memory OFF | Generic answer; panel says memory is off |
| B3 | Toggle deep analysis ON | Pattern analysis expander appears (slower) |
| B4 | Submit feedback | "Saved as INC-L001" message |
| B5 | Re-run same alert | Answer or memory panel now reflects feedback |

## C. Memory acceptance tests (the ones that win points)
| # | Alert | Must be true with memory ON |
|---|---|---|
| C1 | Demo 1: payments too many clients | Cites INC-0388 (leak after Friday deploy) and notes restart/pool-increase failed. Mentions INC-0412 as a different cause worth ruling out |
| C2 | Demo 2: carts vanishing | Cites INC-0431, names shared Redis, warns that restarting Redis wipes carts |
| C3 | Demo 3: orders lag | Cites INC-0447, warns that adding pods makes it worse |
| C4 | Demo 4: unseen iOS crash | States there is no matching history; invents no incident IDs |
| C5 | Any alert | No cited incident ID exists outside the seeded set or feedback IDs |

## D. Edge cases
| # | Scenario | Expected |
|---|---|---|
| D1 | Stop Hindsight, run Analyze | Clear message; app does not crash |
| D2 | Invalid `GROQ_API_KEY` | Clear error after retries |
| D3 | Empty alert | Analyze button disabled |
| D4 | Very long log paste (several thousand characters) | Still answers; note latency |
| D5 | Feedback with empty fields | Saves without crashing |

## E. Latency (record, do not guess)
| Mode | Time |
|---|---|
| Memory OFF | |
| Memory ON (recall) | |
| Memory ON + reflect | |

## Results log
| Date | Test | Pass/Fail | Notes |
|---|---|---|---|
| | | | |

## Failure triage
- **Recall returns unrelated memories:** try `budget="high"`, shorter query, or tag filters.
- **Answer ignores memory:** inspect the MEMORY block sent to Groq; strengthen the system prompt.
- **Seed is slow:** each retain triggers LLM extraction; wait, or check Groq rate limits.
- **`reflect` fails:** confirm the Hindsight server has an LLM configured (it does not work in no-LLM mode).
