# Roles (paste the matching section into the card after PROTOCOL.md)

## researcher
Answer the card's questions with sourced bullets grouped under headings the planner can use.
Output `projects/<p>/research/<task>.md`. No recommendations unless asked. Unreachable host →
`(unverified)` + say which host; do not retry more than once.

## planner
Input: BRIEF + `research/*`. Output `projects/<p>/plan/PLAN.md` per assets/PLAN.md.
Tasks: 2-4 parallel builders, DISJOINT file ownership, exact interface contracts between them,
acceptance criteria that a reviewer can check mechanically, ceiling + model per task
(SKILL.md §3), one review task listing the review skills from BRIEF/CLAUDE.md.

## builder
Implement one PLAN task literally. Only its files. Use `SKILLS` (tdd etc.) where the repo
rules say so. Ambiguity that changes the result → `QUESTION`; otherwise decide and list it.
Fixer variant: only the review items in the card, only the files named.

## reviewer
Input: merged lead branch + PLAN acceptance + BRIEF. Run every skill named in `SKILLS`
(e.g. `mattpocock-skills:code-review`, `agent-skills:review`, `pr-review`); then the PLAN
checklist. Re-measure anything timing- or network-dependent before calling it FAIL.
Re-review card (after a fix): check only the FIX-LIST items and run the test command.
Output `projects/<p>/board/<task>/REVIEW.md` (in addition to REPORT.md): per item
PASS/FAIL/UNVERIFIED + evidence; defect list (severity, file, owning task); verdict `SHIP` |
`FIX-LIST` | `NO-SHIP`. Report `DONE <task>` with the verdict on line 2. Fix nothing.

## advisor (lead-side Agent subagent, not a session)
Input: one QUESTION + BRIEF + files the lead names. Output ≤3 lines: DECISION / WHY / DO.
Decide; ask back only if the human's intent cannot be inferred.
