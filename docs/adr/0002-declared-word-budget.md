# 2. A declared word budget per skill

**2026-09-19. Accepted.** Supersedes the cap clause of
[0001](0001-skill-file-layout.md). The layout that record decided still stands.

## Context

0001 capped `SKILL.md` at 1,000 words, "counted by `wc -w` on the file", and
deferred the check: "The cap is prose until every skill passes, at which point
`build_skills.py` can enforce it — adding the check now would fail the build on
`master`." Migrating the first skill exposed two defects in that.

**The counter does not give one answer.** `wc -w` counts an em dash as a word in
a UTF-8 locale and skips it in the C locale: its single-byte path counts runs of
printable ASCII, and a multibyte character is not printable there. Every file in
this repository uses em dashes, so every figure moves with the environment.
`company-research` measures 1,407 or 1,421. `interview-prep` measures 1,165 or
1,182. `pay-check` measures 986 or exactly 1,000 — under the cap or sitting on
it, depending on the machine that asked. 0001 named `wc -w` to remove an
ambiguity and picked an instrument carrying one of its own.

**The cap never binds.** Enforcement waited on every skill passing, but nothing
brings a skill under a limit that nothing measures, so the deferral renews
itself. `interview-prep` migrated from 1,985 words to 1,165 by moving every
construct-shaped section out, and stopped there. What is left is decisions.

## Decision

`SKILL.md` has a word budget. The default is 1,000. A skill needing more
declares `budget: <n>` in its frontmatter. `build_skills.py` counts the file and
fails the build when it exceeds whichever figure applies.

A word is a whitespace-separated token holding at least one letter or digit.
Markdown punctuation is not a word, and neither is an em dash. The counter lives
in `build_skills.py`, so the number does not depend on the shell that asked.

Raising a budget is a line in a diffed file, argued for in the pull request that
raises it. That is the entire mechanism. A declared figure is not permission to
grow; it is the number to argue down next time the skill is touched.

## Rejected: keep the flat cap and cut to fit

What the cap implies: delete words until the file passes. On `interview-prep`
that meant removing roughly 120 words of decisions, every construct-shaped
section having already moved. That is the failure the cap exists to prevent,
arriving from the other side — a skill losing instruction so a round number can
be met. A limit satisfiable only by deleting the thing it limits is measuring
the wrong quantity.

## Rejected: count the body and exempt the frontmatter

Tempting, because `description` is what a host reads to decide whether to load
the skill at all, and a thin one costs a skill the runs it should have had.
Charging it against the same budget pushes the wrong way.

Rejected because the description is loaded on every run too — in the index,
ahead of the body. Exempting it would hide a real cost rather than remove one.
The budget covers the whole file, and a skill whose description has to be long
declares that in its budget like anything else.

## Consequences

Enforcement starts now instead of after a migration with no end. Two skills
declare a budget the day this lands: `company-research` at 1,400 against 1,383
words, and `interview-prep` at 1,150 against 1,119. Both record where the file
is, not where it should be. `pay-check` at 959 words and `role-fit` at 576 take
the default and declare nothing. Every figure in this paragraph is the counter
above rather than `wc -w`; the two disagree, which is the point.

`build_skills.py` and `plain_check.py` still count differently, and always will.
The second measures the brief a skill produces, not the skill; a figure quoted
from it is not a budget figure.
