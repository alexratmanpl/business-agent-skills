---
name: learning-path
description: Build a learning path to a defined goal in any field — a language, an instrument, a sport, a craft, an exam, a licence, a job skill. Every fact comes from dated, verified research, not memory. Use when someone asks how to learn something, wants a study plan or roadmap, or asks what reaching a level takes and how long. Says plainly when a goal is too vague to plan for, and returns no path rather than a guessed one. Learning only — see role-fit for fit against a named job.
compatibility: The bundled checker needs code execution; without it, the rules in references/plan.md are applied by hand. The fact review is stronger with a subagent and works without one.
---

# Learning Path

Work out what a goal actually demands, prove it from sources, and build only what the evidence supports.

## Stance

- **No path beats a guessed one.** A plan built on an undefined goal or unchecked facts costs someone months. When either is missing, the answer is NO PATH and what would change it — never a list of things to try.
- **Nothing from memory.** Recall says where to look; it is never the source. A fact nobody can open stays out of the plan.
- **The field sets the bar.** An exam board, a regulator, an employer or a governing body defines what good enough means. Where a regulated route exists, the path follows it.
- **Honest about the budget.** Say what their hours buy, even when it is less than they asked for.
- **Performances, not exposure.** A milestone is something they can do that someone else can check.

## Today's date first

Take it from the environment — the system clock, the conversation, the platform. Your own sense of the present ends with your training data. Judge every source against it: what is current, what is superseded, and which version of a standard applies on their deadline.

## Asking

Use whatever interactive choice mechanism the environment offers — tappable options where they exist, plain questions otherwise. Run the intake in passes and skip what is answered. `references/intake.md` holds the passes, the questions and what each digs for.

Ask for evidence of the starting point rather than a self-rating. Once the standard is known, offer a diagnostic built from its real assessment.

## The goal test

Write the goal as seven lines: performance, standard and its judge, conditions, deadline, hours a week, starting point, use. It is defined when the first three let someone else check the result.

If it is not, say so first, in these words: **This goal is not defined enough to build a learning path.** Name the missing lines. Then dig, as `references/intake.md` describes under *When the goal is not defined*. Research what their words mean in practice, and offer two to four concrete versions, each with its judge and its sources.

Still undefined after that: deliver NO PATH, in the format `references/plan.md` sets out. Never fill the gap with generic activity.

**Check that learning is the gate.** Sometimes a licence, years of experience, a portfolio or a closed market blocks the goal, not a skill. If the evidence shows that, say so first. With no skill in the way, the verdict is NO PATH. For a named job, `role-fit` makes that comparison where it is installed.

## Research

Dated, and from the people who set the standard, in this order:

1. The standard, and the version in force on their deadline.
2. How it is judged, and where candidates fail.
3. The route, and the evidence on hours.
4. Every resource the path will use.
5. What is changing inside their window.

Record each fact in the evidence ledger as you find it, with its quote. `references/research.md` holds the source ladder, what counts as independent, the ledger, and what to do when the standard cannot be verified. It governs the research in the goal test too.

**Stop when** the standard, its assessment and the effort evidence are each established or declared unestablished, and every resource has been checked. What is still open is a gap: list it and stop.

## The verdict

Set the evidenced effort against their hours: it fits, it is tight, or it is short. When it is short, say what the hours do buy, as a goal of its own. Build for that only if they accept it; otherwise the verdict is NO PATH. If the milestones later need more than the effort, run the verdict again on their total.

## Build the path

Work backward from the standard, closing the heaviest gaps first. The exit check mirrors the real assessment. Read `references/plan.md` before writing: the format, and what research on practice supports.

## Verify before delivering

Every plan goes through both steps, NO PATH included.

Give the draft to a fresh reviewer: a subagent with no part in writing it. Without one, make a separate pass that opens each source before rereading the claim. Every claim comes back upheld, corrected or dropped. `references/review.md` is its brief, and says how to apply the result.

Then run `scripts/path_check.py` on the plan — `${CLAUDE_SKILL_DIR}/scripts/path_check.py` in Claude Code — and fix what it names until it passes. A row that changes after the review goes back through it.

## Deliver

Write it as markdown, `learning-path-TOPIC.md`, and make sure they have it: attach it, save it to a connected folder, or put it in the reply. Say the date it was checked; after 30 days it wants checking again.

When they bring work back, review it with the second half of `references/review.md`.

## If nobody is watching

Do not stall, and do not invent the person. If the request defines the goal, research the standard and the route, and mark the starting point and hours as missing at the top. If it does not, deliver NO PATH with what would define it.

## Rules

- Where sources conflict, give both and say which is better evidenced.
- Do not explain a finding by guessing at a cause.
- Correct earlier errors plainly, in the plan.
