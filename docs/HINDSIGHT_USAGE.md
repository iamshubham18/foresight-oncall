# How Hindsight memory is used

Memory is the product, not a feature. Without it the agent gives generic advice; with it, the agent
answers like a teammate who was there for every past incident.

## Operations
| Hindsight operation | Where in code | What it does for the user |
|---|---|---|
| `create_bank`, `update_bank_config` | `src/memory.py: setup_bank` | Gives the bank an SRE mission and a skeptical disposition |
| `retain` (post-mortems) | `scripts/seed.py` | Loads incident history, including fixes that failed |
| `retain` (environment facts) | `scripts/seed.py` | Durable context: Friday deploys, shared Redis, flag service |
| `retain` (live feedback) | `src/agent.py: retain_feedback` | The learning loop: engineer corrections become memory |
| `recall` | `src/agent.py: analyze` | Finds past incidents similar to a new alert, even when worded differently |
| `reflect` | `src/agent.py: analyze (deep)` | Reasons across incidents to find recurring patterns |

## Why this needs memory and not just a prompt
1. **Different wording, same failure.** The demo alert says `too many clients already`; the stored
   incidents say `HikariPool ... not available` and `max_client_conn`. Recall must bridge that gap.
2. **Same symptom, different cause.** INC-0388 was an app leak; INC-0412 was a pooler limit. The agent
   must not collapse them into one story.
3. **Negative knowledge.** "Restarting only helped for 15 minutes" is retained and surfaced.
4. **Compounding.** Feedback from today's incident is available to tomorrow's alert.

## What to show judges
| Moment | Where to look |
|---|---|
| Generic answer, no memory | Toggle OFF in the sidebar |
| Specific, cited answer | Toggle ON; recommendation cites INC-IDs |
| Which memories were used | Memory panel on the right |
| Honest uncertainty | Demo alert 4 (unseen failure) |
| Learning | Submit feedback, re-run the same alert |
| The stored knowledge graph | Hindsight UI at `http://localhost:9999` |

## Before / after (to be recorded during testing)
| Alert | Memory OFF | Memory ON |
|---|---|---|
| payments-api, too many clients | _fill in after test_ | _fill in after test_ |
| checkout carts vanishing | _fill in after test_ | _fill in after test_ |
| orders consumer lag | _fill in after test_ | _fill in after test_ |
| unseen iOS crash | _fill in after test_ | _fill in after test_ |
