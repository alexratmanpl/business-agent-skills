# Agent instructions

Four Agent Skills for business and career work, built on the
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

`SKILL.md` is loaded in full on every run, so its length is a cost paid every time: it is capped
at 1,000 words, counted by `wc -w` on the file. An addition that would breach the cap means a
construct-shaped section moves to `references/` first — not that the addition is dropped.

A rule a script can enforce belongs in the script, with one line in `SKILL.md` to run it. Prose
restating a shipped check is one rule in two places.

No two sections in one skill may be read as the same step. An agent told to add something to the
step that asks the user for input must have exactly one candidate section.

Why this shape, and what was rejected:
[docs/adr/0001-skill-file-layout.md](docs/adr/0001-skill-file-layout.md).
