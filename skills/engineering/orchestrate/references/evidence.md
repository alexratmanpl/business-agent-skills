# orchestrate

Lead session + budget-capped cloud worker sessions on a Claude subscription. No API key, no
framework. Install: copy this folder to `.claude/skills/orchestrate/`; in each target repo copy
`scripts/orch-ceiling.sh` to `.claude/hooks/` and merge `assets/settings.snippet.json` into
`.claude/settings.json` (the lead does this itself in §0 if missing). Use: write
`projects/<name>/BRIEF.md` (assets/BRIEF.md), open a cloud session, `/orchestrate <name>`.

## Evidence (projects/cities, 2026-11-02)
11 workers, 1 lead, ~25 min, site shipped from zero knowledge. ~85k context and ~$0.25 list
per worker on sonnet. Budgets honoured 11/11. HANDOVER → successor worked from the file alone.
One messaging failure (wrong tool) recovered by the REPORT.md fallback + lead check-in.
Reviewer FAILs: 2 of 3 false alarms, caught by lead re-verification; no fixer spawned.
Workers compress (edit+test+commit in one call): tool-call caps don't bound tokens; the
ceiling hook does.

## Evidence 2-4 (same day, skill invoked by name from fresh sessions, `/orchestrate <p>` only)
| run | tier | lead | workers | total (list $) | time | result |
|---|---|---|---|---|---|---|
| laptops, fable lead set by hand | – | $10.43, 235k ctx | 11, $3.59 | 14.02 | 23 min | 39 tests, SHIP |
| laptops2, auto RISK 2 | low | sonnet $1.13 | 8, $2.39 | 3.52 | 12 min | 31 tests, SHIP |
| fx-ui (money UI + mock API), auto RISK 3 | high | sonnet $0.32 → fable $14.39 (old self-promotion rule) | 12, $29.64 (8 fable) | 44.35 | 70 min | 39 tests, SHIP, 3 reviewer-found bugs fixed |

Per session: haiku ~$0.01, sonnet $0.25-0.50, fable $1.7-5.0. Findings folded into the skill:
preflight for hosts and skills before any spawn; skills must be in the repo (user plugins are
not inherited by fresh clones; built-ins are); haiku floor 80k and never on integration tasks;
fable needs ~1.5× ceilings (3 of 3 fx-ui handovers were fable at 90-100k); re-review scoped to
FIX-LIST items on mid tier (full fable re-reviews were ~$10 of $44); the lead stays mid tier,
judgment goes to a high-tier advisor subagent (the fable lead was the dearest session in every
run it appeared in); gate sends a plan summary, not the plan; finished sessions archived.

## Limits
Ceiling is a hook warning, not a hard stop (hard stop only in `claude -p --max-turns` locally).
Rate limits are account-wide: ≤4 concurrent workers. Workers report at end of turn only;
`send_message` reaches them mid-run, `list_events` inspects a silent one.
