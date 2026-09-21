# Agent instructions

Five Agent Skills for business and career work, built on the
[Agent Skills open standard](https://agentskills.io).

Skills live at `skills/<category>/<skill-name>/SKILL.md`. Categories organise the repo only —
installing flattens them into one directory, so skill names must be unique across every category.

## What goes where

A skill is one directory. Which file a thing belongs in follows from when it is read:

| Path | Holds | Read |
| :--- | :--- | :--- |
| `SKILL.md` | what the agent must **choose** — the steps, the questions, when to stop | in full, every time the skill fires |
| `references/<topic>.md` | what the agent must **construct** — the shape of an output, how a bundled file works | only at the step that needs it |
| `scripts/` | what can be **checked** rather than read | run, never read |
| `assets/` | templates and fixtures the skill ships | as used |

`SKILL.md` is loaded in full on every run, so its length is a cost paid every time. Every skill
has a word budget: 1,000 by default, or whatever `budget:` in its frontmatter declares.
`build_skills.py` counts the file and fails the build when it is over. An addition that would
breach the budget means a construct-shaped section moves to `references/` first — not that the
addition is dropped. Raise the budget only when nothing is left to move, and say why in the
pull request.

A rule a script can enforce belongs in the script, with one line in `SKILL.md` to run it. Prose
restating a shipped check is one rule in two places.

No two sections in one skill may be read as the same step. An agent told to add something to the
step that asks the user for input must have exactly one candidate section.

Why this shape, and what was rejected: [the decision records](docs/adr/).
