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
| fixer (review items of one task, a merge conflict, or env) | mid 100k | mid 100k | 10 min |
| advisor (Agent subagent, not a session) | mid | high | – |
| lead | mid 350k | mid 350k (judgment goes to the advisor, not to a dearer lead) | – |

High-tier models spend ~1.5× the context of mid for the same task (reasoning tokens), hence
the larger ceilings. Ids are the current ones; BRIEF `Models` overrides. Integration tasks (touch every module) are
never haiku.

## Preflight (run at §0.6, before any spawn)
- Hosts: every entry in BRIEF `network hosts` gets one `curl -sI`. A refusal from the proxy is
  "denied"; the lead reports it with the allowlist steps.
- Skills: every entry in BRIEF `Skills` must be a Claude Code built-in or exist in the repo as
  `.claude/skills/<name>/` or an `enabledPlugins` entry in `.claude/settings.json` (workers are
  fresh clones and see no user-level plugins).

## Spawn sequence (lead side, every spawn)
1. ONE Bash call: BOARD row + LOG `SPAWN` + commit + push. Workers clone the lead branch, so
   pending merges and handovers must be pushed before this call.
2. `create_session` as above; its id goes into the BOARD row at the next bookkeeping call.
3. `send_later(<wave timeout from the tier table>, "LEAD check-in <tasks>")`: one check-in per
   wave, deleted when the wave reports.

## Successor
Same role, ceiling ×1.5, same model (haiku → sonnet after one handover); at most 3 successors
per task, 2 at high risk, then BLOCKED. Task id `<task>b`, then `c`, `d` (title, branch and board dir follow the id); CARD
`CONTINUE_FROM` = the predecessor's HANDOVER.md.

## Lead succession
Write `board/LEAD-HANDOVER.md` per `assets/HANDOVER.md` with task-id `LEAD`; commit + push; then
`create_session(title="<project> LEAD", model=<mid id>, prompt="/orchestrate <project> --resume")`
(role lead). The successor books your cost at resume (Cost accounting).

## Target repo setup (checked at §0.4, installed on the lead branch)
- `.claude/hooks/orch-ceiling.sh`: copy of `scripts/orch-ceiling.sh`.
- `.claude/settings.json`: the hook entries from `assets/settings.snippet.json`.
- `.gitignore`: a `.orch/` line (each session writes its own ceiling there).

## Card budgeting
Name the model on every spawn. Worker overhead is 40-60k (protocol + roles + card + PLAN +
reads), so the card's `read` lists extracts (`sed -n`, `grep`, `node -e`) rather than whole
files, and no task gets a ceiling under 80k. Add `CALLS` to the card when a task is dominated
by unbatchable calls (web searches) or when the target repo has no hook.
Fixer card `read` = its REVIEW.md item lines (conflict/env fixer: the failing merge or test
output instead) + extracts of its owned files + the PLAN `## Contracts` lines for its
interface; nothing else. Reviewer spawn: `clone_depth` =
`git rev-list --count <DIFF_BASE>..HEAD` + 5, so `DIFF_BASE` exists in its clone.

## Cost accounting
Every session reports its own usage: `get_session(<id>)` → `external_metadata.usage.cost_usd`
(list-price equivalent; on a subscription it is rate-limit consumption) and
`external_metadata.context_usage.used_tokens`. Book it in the same Bash call as the BOARD update:
- On DONE/HANDOVER/BLOCKED of a worker: fill the BOARD `cost` column as `$<cost_usd>/<used_tokens>k`.
- At CLOSE: every BOARD row has a session id and a cost (cross-check with `list_sessions`
  tag `orch:<project>`); missing → `get_session` it now; `$0 never ran` only if it never
  started. Then `get_session` with no id for your own cost; LOG
  `COST total=$<sum> lead=$<own> workers=$<sum of rows> sessions=<n> tokens=<sum>k`; append one row
  to `projects/COSTS.md` (create from `assets/COSTS.md` if missing); commit with the CLOSE.
- A lead successor books the predecessor lead's cost at resume (its id is in LEAD-HANDOVER.md).
The ledger is the comparison across runs: same project, different tier, different skill version.

## Reviewer blocked on the test command
Run the PLAN `## Test command` on the lead branch yourself. It cannot run (setup, interpreter,
missing dependency) → one env fixer owning T0's files, before any re-review. It runs but tests
fail → that is a review FAIL for the owning task, not an environment problem.

## Silent worker (no message by the wave check-in)
1. `get_session(<id>)`: `status_bucket` and `post_turn_summary`.
2. `list_events(session_id, kinds=["assistant","result"], limit=100)`: last turn's text.
3. Fetch its branch; read `board/<task>/REPORT.md` or `HANDOVER.md`: the message may have
   failed while the file landed.
4. Failed to start → book `$0 never ran`, respawn the same card. Blocked on a permission
   prompt: book its cost (`get_session`), `interrupt_session`, `archive_session`, read the
   prompt's tool in `list_events`: a specific tool → add it to the lead branch's
   `.claude/settings.json` allow list, respawn, list the entry in the CLOSE report (it
   persists); an edit/Bash-class prompt → the lead's own mode is interactive and workers
   inherit it: LOG `ESCALATE`, tell the human to restart the lead in `auto` or `acceptEdits`.
   Still running under ceiling → extend the check-in once; over ceiling → `send_message`
   "HANDOVER now", wait one check-in, then treat as failed.
