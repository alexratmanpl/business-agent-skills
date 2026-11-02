---
name: orchestrate
description: Run a project as a LEAD session that spawns short, budget-capped Claude Code cloud worker sessions (research, plan, build, review), merges their branches, answers their questions and respawns successors on budget exhaustion. Use when asked to "orchestrate", "run project <name>", or to work a BRIEF.md unattended on a subscription.
compatibility: Needs Claude Code cloud sessions (the claude-code-remote tools create_session, send_message, send_later, get_session) and git. The ceiling hook needs bash and jq in the target repo; where the hook file is absent, workers self-check context with get_session (context_usage.used_tokens) at each step boundary.
---

# orchestrate: LEAD instructions

All paths below are under `projects/<project>/` unless they start with `.claude/`.

You are the LEAD. You talk to the human; workers talk only to you. Workers are cloud sessions
(`mcp__claude-code-remote__create_session`), one per task, each on its own branch. State lives in
git under `projects/<project>/` so any lead can take over.

Read `references/` (protocol, roles, spawn) and `assets/` (fixed formats, never reshaped) at the
step that needs them.

## 0. Start / resume
1. `projects/<project>/BRIEF.md` must match `assets/BRIEF.md`. Missing → write it with the
   human; free text from them is fitted to the template by you.
2. If `board/BOARD.md` exists you are resuming: read BOARD, LOG (last 40 lines),
   `board/LEAD-HANDOVER.md` if present. Else create BOARD and LOG from templates.
3. Read the repo's `CLAUDE.md`/`AGENTS.md` once: rules and skill names go into every card
   (`RULES`, `SKILLS` fields). Never restate them in your own words.
4. Hook: the target repo must hold a copy of `scripts/orch-ceiling.sh` at .claude/hooks/ and
   the hook entries from `assets/settings.snippet.json` in its .claude/settings.json, and
   `.orch/` in its .gitignore. Missing → add them on the lead branch, commit, push, before the
   first spawn. Workers are fresh clones; they get only what is committed.
5. Preflight, before any spawn: (a) every host in BRIEF `network hosts` → one `curl -sI`;
   denied → LOG `ESCALATE` now with the allowlist steps, and ask the human whether to run
   search-only with facts flagged (unverified). (b) every skill in BRIEF `Skills` must be a
   Claude Code built-in or exist in the repo (`.claude/skills/<name>/` or `enabledPlugins` in
   .claude/settings.json); missing → LOG `ESCALATE`; if the human declines, the review is
   "formally incomplete" in LOG and the CLOSE report.
6. Risk: score BRIEF per the rubric in `assets/BRIEF.md` (one point per signal; ≥3 = high),
   LOG `RISK <n> <signals>`. The score picks the worker tier column in `references/spawn.md`;
   it may be raised later, never lowered. You stay on the mid tier whatever the score. High:
   send a ≤10-line PLAN summary + path as `ESCALATE` and wait for the human before BUILD;
   every DECISION that alters the plan or waives a review FAIL goes through the advisor first.
7. Record your session id (`get_session` with no id) in BOARD header. Set your own ceiling:
   `mkdir -p .orch && echo 350000 > .orch/ceiling` (`.orch/` is git-ignored).

## 1. Loop
RESEARCH → PLAN → BUILD → REVIEW → (FIX → RE-REVIEW)×≤2 → CLOSE. Skip RESEARCH when BRIEF
`Unspecified` is empty. One planner. Builders in parallel, ≤4 concurrent. Review is mandatory
and runs the skills named in BRIEF/CLAUDE.md; a review without them is invalid. Re-review after a fix
covers the FIX-LIST items and the test command only; the full checklist runs on the first
review and after a `NO-SHIP`.

Spawn: BOARD row + LOG `SPAWN` + commit + push in ONE Bash call (workers clone the lead
branch: merges and handovers must be pushed first), then `create_session` per
`references/spawn.md`, then `send_later(<wave timeout>, "LEAD check-in <tasks>")`. Every
bookkeeping event is one Bash call (board, log with `date -u +%H:%M`, commit, push).
Wave timeouts are in spawn.md. One check-in per wave, delete it when the wave reports. Archiving (`archive_session`) happens on DONE/HANDOVER as §2 says and at
CLOSE for whatever remains not running, LOG `ARCHIVE <n>`; BRIEF `Keep sessions: yes` turns
all of it off.

## 2. On worker message (first line is the token)
| token | do |
|---|---|
| `DONE <t>` | fetch+merge `agents/<p>/<t>` into lead branch; conflict → do not resolve by hand, spawn a fixer owning the conflicting files; BOARD done; LOG `DONE`; `archive_session(<t>)`; next. Reviewer DONE carries the verdict on line 2 (`SHIP`/`FIX-LIST`/`NO-SHIP`) |
| `HANDOVER <t>` | merge, push; read `board/<t>/HANDOVER.md`; spawn `<t>b` (then c, d) with CARD `CONTINUE_FROM`; ceiling ×1.5; answer its open questions in the card; archive `<t>`; LOG `RESPAWN`. After 3 successors (2 at high risk) → `BLOCKED` |
| `QUESTION <t>` | trivial → answer; else run `advisor` as an Agent subagent (fresh context, tier per spawn.md) with the question + BRIEF; `send_message(worker, "ANSWER: …")`; LOG `DECISION`. Advisor cannot decide, or a 2nd HANDOVER on one task, or NO-SHIP → raise RISK |
| `BLOCKED <t>` | give missing input or split the task; else LOG `ESCALATE` and tell the human |
| nothing by check-in | inspect per spawn.md "Silent worker", then act on what you find as above |
Review `FAIL`s: re-verify each yourself before spawning a fixer; waive false alarms with LOG
`DECISION` (high risk: advisor first). Fixer card = review items only, owns only the files named.

## 3. Budgets and models
Ceiling = context tokens; the hook warns at ceiling and every 20k after. Ceilings, model ids,
wave timeouts and card budgeting rules: `references/spawn.md`, read at every spawn.

## 4. Lead succession
When the hook says you are past ceiling: finish the step in hand, write
`board/LEAD-HANDOVER.md` (assets/HANDOVER.md, task-id LEAD), commit+push, then
`create_session` per `references/spawn.md` (role lead, prompt `/orchestrate <project>
--resume`), LOG `LEAD-SUCCESSION <new id>`, tell the human the new session id, stop.

## 5. Report to the human
Only at CLOSE, `ESCALATE`, or when asked: what shipped, DECISION lines since last report,
open ESCALATE items, sessions spawned and archived. Three to ten lines. Never forward worker
transcripts.

## Hard rules
Merge only branches whose task reported DONE. Never edit a worker's files yourself; spawn.
Never skip review. Never commit to `main`; the lead branch is the integration branch, the
human merges it. Every DECISION and ESCALATE is a LOG line before anything else happens.
