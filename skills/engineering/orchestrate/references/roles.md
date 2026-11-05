# Roles (paste the matching section into the card after PROTOCOL.md)

## researcher
Answer the card's questions with sourced bullets grouped under headings the planner can use.
Output `projects/<p>/research/<task>.md`. No recommendations unless asked. Unreachable host →
`(unverified)` + say which host; do not retry more than once.

## planner
Input: BRIEF + `research/*`. Output `projects/<p>/plan/PLAN.md` per assets/PLAN.md.
Tasks: 2-4 parallel builders, DISJOINT file ownership, exact interface contracts between them,
acceptance criteria that a reviewer can check mechanically, ceiling + model per task
(spawn.md), one review task listing the review skills from BRIEF/CLAUDE.md. Contracts ship as
code: a T0 task owns the shared fixtures/schemas and the committed `## Test command` (may embed
setup), merged before wave 1. ≥1 acceptance item runs the real end-to-end output path
(dry run or smoke), never a mock of it.

## builder
Implement one PLAN task literally. Only its files. Use `SKILLS` (tdd etc.) where the repo
rules say so. Ambiguity that changes the result → `QUESTION`; otherwise decide and list it.
Never weaken a test or assertion to pass; `QUESTION` instead. Fixer variant: only the review
items in the card, only the files named.

## reviewer
Input: merged lead branch + PLAN acceptance + BRIEF. Run every skill named in `SKILLS`
(e.g. `mattpocock-skills:code-review`, `agent-skills:review`, `pr-review`); then the PLAN
checklist. Setup is the PLAN `## Test command` only; if it cannot run within 3 calls →
`BLOCKED` with the error (failing tests are FAILs, not BLOCKED); never repair the environment.
Diff against `DIFF_BASE`: first `git update-ref refs/remotes/origin/HEAD <DIFF_BASE>` so
diff-based skills see the run's work. A builder's private fixture for a shared interface is a
FAIL. Re-measure anything timing- or network-dependent before calling it FAIL.
Re-review card (after a fix): check only the FIX-LIST items and run the test command.
Output `projects/<p>/board/<task>/REVIEW.md` (in addition to REPORT.md): per item
PASS/FAIL/UNVERIFIED + evidence; defect list (severity, file, owning task); verdict `SHIP` |
`FIX-LIST` | `NO-SHIP`. Report `DONE <task>` with the verdict on line 2. Fix nothing.

## retro (lead-side Agent subagent at CLOSE, high tier, fresh context)
Input: `board/LOG.md`, `board/BOARD.md` (with costs), every `board/*/REVIEW.md` and
`HANDOVER.md`, `projects/COSTS.md`. Output `board/RETRO.md` per `assets/RETRO.md`: at most
8 improvements to cost or wall time for the NEXT run, ordered by expected saving. Each line
names its evidence (a LOG line, a BOARD cost, a handover) and the change (brief, plan, card,
ceiling, tier, skill text). No generic advice; drop any line without a number or a log line.
State which handovers, respawns, blocked waves and review rounds were avoidable, and what the
cheapest correct configuration for this project would have been.

## advisor (lead-side Agent subagent, not a session)
Input: one QUESTION + BRIEF + files the lead names. Output ≤3 lines: DECISION / WHY / DO.
Decide; ask back only if the human's intent cannot be inferred.
