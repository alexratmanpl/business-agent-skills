# 1. One layout for every skill

**2026-09-19. Accepted.**

## Context

A scheduled run could not add anything to `interview-prep`. Four findings against it were read
and judged real; three changes were written and measured; the review returned not ready six
times, and three of those rounds had its two axes give contradictory instructions about the same
sentence. Underneath the disagreement, every review reported the same thing independently: each
addition duplicated something already in the file.

The file was 1,985 words. Three of its sections held 64% of that, and only one of the three was
instruction — the other two documented an output format and a bundled HTML file. Both are
material an agent needs only once it has reached a particular step, and both were being loaded
in full on every run that touched the skill.

It is not alone. `company-research` is 1,407 words. `role-fit` is 603 and `pay-check` is 986, so
a thousand words is demonstrably enough for a complete skill in this repository. Every figure here
is `wc -w` on `SKILL.md`; the bundled prose checker counts differently, which is why the rule
names its counter.

Two smaller problems point the same way. No skill uses `references/`, though the Agent Skills
standard defines it and loads it on demand. And `pay-check` has three sections — `Asking`,
`Ask first` and `If asked first` — that an agent asked to extend "the asking step" could each
reasonably pick.

## Decision

`AGENTS.md` carries the operative rule; this file records why it was chosen. A later change to
the rule is a new record superseding this one, not an edit to it.

One layout: `SKILL.md` holds what the agent must choose, `references/` holds what it must
construct, `scripts/` holds what can be checked instead of read. `SKILL.md` is capped at 1,000
words, and an addition that would breach the cap moves a section rather than being dropped.

## Rejected: split a large skill into several skills

The obvious alternative. Skill names flatten on install, so a second skill is a second thing to
install and keep in step, and `interview-prep` is the orchestrator that calls the other three —
halving it weakens the one place that coordinates them.

More decisively, it would not have fixed the deadlock. That was caused by additions duplicating
text already present, not by the skill covering too many topics. Splitting moves duplication
across a boundary; moving reference material out removes it.

## Consequences

Two of the four skills on `master` exceed the cap and migrate when next touched, largest first.
A skill added later is written to the layout rather than migrated into it. The cap is prose until
every skill passes, at which point `build_skills.py` can enforce it — adding the check now would
fail the build on `master`.
