# Spawn (read at every spawn)

```
create_session(
  title="<project>/<task> <role>",
  model=<id from table>,
  source_url=<repo url>, source_revision=<lead branch>,
  outcome_branch="agents/<project>/<task>",
  tags=["orch:<project>","orch:role:<role>"],
  permission_mode=<omit to inherit the lead's; never "plan": a worker stalls at the prompt>,
  prompt=<references/protocol.md> + <role section of references/roles.md> + <assets/CARD.md filled>)
```
Lead successor: `title="<project> LEAD"`, `model=<mid id>`, `prompt="/orchestrate <project> --resume"`.

Tiers: low = claude-haiku-5-5, mid = claude-sonnet-5-5, high = claude-fable-5-1 (or
claude-opus-5-5). The RISK score from §0 picks the column.

| role | RISK low (<3): tier, ceiling | RISK high (≥3): tier, ceiling | wave timeout |
|---|---|---|---|
| researcher, simple (≤3 questions, no judgment) | low 80k | mid 90k | 8 min |
| researcher | mid 90k | mid 90k | 8 min |
| planner | mid 90k | high 135k | 6 min |
| builder, simple (1 file, ≤2 reads, mechanical) | low 80k | mid 90k | 10 min |
| builder | mid 120k | mid 120k | 10 min |
| builder touching money/auth/security/migration files | mid 120k | high 150k | 10 min |
| reviewer, first review or after NO-SHIP | mid 100k | high 150k | 8 min |
| re-reviewer (FIX-LIST items + test command) | mid 90k | mid 90k | 8 min |
| advisor (Agent subagent, not a session) | mid | high | – |
| lead | mid 350k | mid 350k (judgment goes to the advisor, not to a dearer lead) | – |

High-tier models spend ~1.5× the context of mid for the same task (reasoning tokens), hence
the larger ceilings. Ids are the current ones; BRIEF `Models` overrides. Integration tasks (touch every module) are
never haiku. Successor: same role, ceiling ×1.5, same model (haiku → sonnet after one handover);
at most 3 successors per task, 2 at high risk, then BLOCKED.

## Card budgeting
Name the model on every spawn. Worker overhead is 40-60k (protocol + roles + card + PLAN +
reads), so the card's `read` lists extracts (`sed -n`, `grep`, `node -e`) rather than whole
files, and no task gets a ceiling under 80k. Add `CALLS` to the card when a task is dominated
by unbatchable calls (web searches) or when the target repo has no hook.

## Cost accounting
Every session reports its own usage: `get_session(<id>)` → `external_metadata.usage.cost_usd`
(list-price equivalent; on a subscription it is rate-limit consumption) and
`external_metadata.context_usage.used_tokens`. Book it in the same Bash call as the BOARD update:
- On DONE/HANDOVER/BLOCKED of a worker: fill the BOARD `cost` column as `$<cost_usd>/<used_tokens>k`.
- At CLOSE: `get_session` with no id for your own cost; LOG
  `COST total=$<sum> lead=$<own> workers=$<sum of rows> sessions=<n> tokens=<sum>k`; append one row
  to `projects/COSTS.md` (create from `assets/COSTS.md` if missing); commit with the CLOSE.
- A lead successor books the predecessor lead's cost at resume (its id is in LEAD-HANDOVER.md).
The ledger is the comparison across runs: same project, different tier, different skill version.

## Silent worker (no message by the wave check-in)
1. `get_session(<id>)`: `status_bucket` and `post_turn_summary`.
2. `list_events(session_id, kinds=["assistant","result"], limit=100)`: last turn's text.
3. Fetch its branch; read `board/<task>/REPORT.md` or `HANDOVER.md`: the message may have
   failed while the file landed.
4. Failed to start → respawn the same card. Blocked on a permission prompt → the lead's own
   mode is interactive and workers inherit it: `interrupt_session`, `archive_session`, LOG
   `ESCALATE`, tell the human to restart the lead in a non-interactive mode (`auto` or
   `acceptEdits`); a worker cannot be given a mode the lead lacks.
   Still running under ceiling → extend the check-in once; over ceiling → `send_message`
   "HANDOVER now", wait one check-in, then treat as failed.
