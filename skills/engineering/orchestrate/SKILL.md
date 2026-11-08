---
name: orchestrate
description: Run a project as a LEAD session that spawns short, budget-capped Claude Code cloud worker sessions (research, plan, build, review), merges their branches, answers their questions and respawns successors on budget exhaustion. Use when asked to "orchestrate", "run project <name>", or to work a BRIEF.md unattended on a subscription.
compatibility: Needs Claude Code cloud sessions (the claude-code-remote tools create_session, send_message, send_later, get_session) and git. The ceiling hook needs bash and jq in the target repo; where the hook file is absent, workers self-check context with get_session (context_usage.used_tokens) at each step boundary.
---

# orchestrate: LEAD instructions

You are the LEAD: you talk to the human, workers talk only to you. A worker is one cloud
session (`mcp__claude-code-remote__create_session`) per task on its own branch. State lives in
git under `projects/<project>/` (paths below are relative to it unless they start with
`.claude/` or `.orch/`) so any lead can take over. Read `references/` and `assets/` (fixed formats, never
reshaped) at the step that needs them.

## 0. Start / resume
1. `BRIEF.md` must match `assets/BRIEF.md`; missing → write it with the human from their
   free text.
2. `board/BOARD.md` exists → resuming: read BOARD, the last 40 LOG lines, and
   `board/LEAD-HANDOVER.md` if present; else create BOARD and LOG from the templates. Then,
   before anything else, put your session id (`get_session`, no id) in the BOARD header:
   stale headers get live leads archived.
3. Read the repo's `CLAUDE.md`/`AGENTS.md` once; its rules and skill names go into every
   card's `RULES` and `SKILLS` fields.
4. Target repo setup per spawn.md "Target repo setup"; missing → add, commit, push on the
   lead branch before the first spawn: workers get only what is committed.
5. Set your own ceiling: `mkdir -p .orch && echo 350000 > .orch/ceiling`.
6. Preflight per spawn.md "Preflight" before any spawn. Host denied → LOG `ESCALATE` now with
   the allowlist steps; ask the human whether to run search-only with facts flagged
   `(unverified)`. Skill missing → LOG `ESCALATE`; human declines → the review is "formally
   incomplete" (it needs every skill in BRIEF/`CLAUDE.md`): say so in LOG and the CLOSE report.
7. Risk: score BRIEF by the rubric in `assets/BRIEF.md` (one point per signal, ≥3 = high), LOG
   `RISK <n> <signals>`. It picks the worker tier column in spawn.md; §2 may raise it, nothing
   lowers it; you stay on the mid tier. High: after PLAN, send a ≤10-line summary + the PLAN
   path as `ESCALATE`; wait for the human before BUILD; DECISIONs that alter the plan
   or waive a review FAIL go through the advisor first.

## 1. Loop
RESEARCH → PLAN → BUILD → REVIEW → (FIX → RE-REVIEW)×≤2 → CLOSE. Skip RESEARCH when BRIEF
`Unspecified` is empty. One planner; builders in parallel, ≤4 concurrent. Review is formally
incomplete without the skills named in BRIEF/`CLAUDE.md`. First review and any review after
`NO-SHIP`: full checklist; re-review after a fix: FIX-LIST items and the
test command only.

Each bookkeeping event is one Bash call: BOARD, LOG line stamped `date -u +%H:%M`, commit,
push. Spawn per spawn.md "Spawn sequence" (LOG `SPAWN`; one check-in per wave, deleted on
report). Before the first builder spawn LOG `BUILD-BASE <sha>` (the reviewers' `DIFF_BASE`).

Archive only sessions in this project's BOARD, each after a fresh `get_session` shows it not
running, never from memory; BRIEF `Keep sessions: yes` turns archiving off.

CLOSE: spawn.md "Cost accounting" (LOG `COST`); sweep remaining sessions, LOG
`ARCHIVE <n>`; run `retro` (roles.md) as a high-tier Agent subagent; commit `board/RETRO.md`.

## 2. On worker message (first line is the token)
| token | do |
|---|---|
| `DONE <t>` | fetch+merge `agents/<p>/<t>` into the lead branch; conflict → fixer owning the conflicting files; BOARD done + cost (spawn.md "Cost accounting"); LOG `DONE`; `archive_session(<t>)`. A reviewer's line 2 is the verdict: `SHIP` / `FIX-LIST` / `NO-SHIP` |
| `HANDOVER <t>` | merge, push; read `board/<t>/HANDOVER.md`; spawn `<t>b` (then c, d) per spawn.md "Successor", CARD `CONTINUE_FROM`, open questions answered in the card; book cost, archive `<t>`; LOG `RESPAWN`. Successor cap hit → BOARD `partial merged`, handle as `BLOCKED`, name it in the CLOSE report |
| `QUESTION <t>` | trivial → answer; else `advisor` (roles.md) as a fresh-context Agent subagent, tier per spawn.md, with the question + BRIEF; `send_message(worker, "ANSWER: …")`; LOG `DECISION` |
| `BLOCKED <t>` | supply the missing input or split the task; reviewer blocked on the test command → spawn.md "Reviewer blocked"; else LOG `ESCALATE` and tell the human |
| nothing by check-in | inspect per spawn.md "Silent worker", then act as above |

Raise RISK when the advisor cannot decide, a task hits its 2nd HANDOVER, or a review says
`NO-SHIP`. Review `FAIL`s: re-verify each yourself before spawning a fixer; waive false alarms
with LOG `DECISION` (high risk: advisor first). One fixer per owning task per round;
cross-task items and merge conflicts → one fixer owning the named files (spawn.md fixer row).

## 3. Budgets and models
Ceiling = context tokens; the hook warns at it and every 20k after. Ceilings, model ids,
wave timeouts, card budgeting: spawn.md, read at every spawn.

## 4. Lead succession
Past ceiling (hook warning): finish the step in hand, hand over per spawn.md "Lead
succession", LOG `LEAD-SUCCESSION <new id>`, tell the human the new session id, stop.

## 5. Report to the human
Only at CLOSE, on `ESCALATE`, or when asked: what shipped, DECISION lines since the last
report, open ESCALATE items, sessions spawned and archived, the `COST` line, RETRO's top
three. Never forward worker transcripts.

## Hard rules
Merge only branches whose task reported DONE or HANDOVER (the latter only seeds the successor). Never edit a worker's files or
hand-resolve its conflicts; spawn. Never skip review. Never commit to `main`: the lead branch
is the integration branch, merged by the human. Every DECISION and ESCALATE is a LOG line
before anything else happens.
