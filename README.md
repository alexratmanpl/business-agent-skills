# Business & Career Skills

Five Agent Skills for business and career work: research a company, judge whether you fit a role,
prepare for the interview, get the money right, and plan how to learn what a goal demands. Honest
rather than encouraging — they are written to tell someone a stretch is a stretch.

Each skill is a `SKILL.md` with frontmatter plus the files it needs, following the
[Agent Skills open standard](https://agentskills.io).

## The skills

| Skill | Does | Bundles |
| :--- | :--- | :--- |
| [`company-research`](skills/business/company-research/) | What a company really does, how healthy it is, who it competes with, what staff say. Produces a plain-language dossier. | — |
| [`role-fit`](skills/careers/role-fit/) | Compares a background against a specific job: a verdict, a rough probability, the gaps, and the unusual strength other applicants lack. | — |
| [`pay-check`](skills/careers/pay-check/) | Local market rate for role, level and contract type; employment-versus-contracting conversion; how to reopen a number already given. | `scripts/rate_calc.py`, `rates-example.json` |
| [`interview-prep`](skills/careers/interview-prep/) | Preparation at any stage, a one-to-two page brief to read beforehand, and a page for notes during the call. Calls the other three by name when they are installed, and works alone when they are not. | `scripts/plain_check.py`, `interview-record.html` |
| [`learning-path`](skills/learning/learning-path/) | A learning path to a defined goal in any field — a language, an instrument, a sport, an exam, a job skill — built from dated research that every milestone cites. Tests the goal first, sets the hours against the evidence, and returns no path rather than a guessed one. | `scripts/path_check.py` |

Invoke one by name, or describe the task and let the agent choose.

`pay-check`, `interview-prep` and `learning-path` carry a `compatibility` line in their
frontmatter: their bundled scripts need code execution, and each says what to do instead where
there is none.

## Install

Copy a skill's directory — `SKILL.md` and everything beside it — into wherever the agent reads
skills from. Packaged `.skill` archives for all five are attached to the `latest` release, which
CI rebuilds from `master` on every push.

## Layout

```
skills/
├── business/
│   └── company-research/
├── careers/
│   ├── role-fit/
│   ├── pay-check/
│   └── interview-prep/
└── learning/
    └── learning-path/
```

Categories organise this repository only. Installing flattens them, so skill names must be unique
across all categories.

## Development

`python3 scripts/build_skills.py --check-only` validates every skill: frontmatter parses and has a
name and description, the name matches the directory that gets installed, every bundled file the
body points at exists, the body is not still a placeholder, and `SKILL.md` fits its word budget.
Drop `--check-only` to write `.skill` archives to `dist/`. CI runs it on every pull request.

`skills/careers/interview-prep/scripts/plain_check.py` reads a drafted brief — or the skill's own
prose — for long sentences, abbreviations used before being spelled out, machine phrasing and
excess length. It reports and exits zero; it is a checklist, not a gate.

`skills/learning/learning-path/scripts/path_check.py` reads a drafted learning plan and fails on a
fact with no source or date, a source read more than 30 days ago, a standard nobody verified, a
milestone resting on nothing confirmed, an outcome that is an activity rather than a performance,
hours that fall short of the evidenced effort or the budget verdict, and a NO PATH plan that
carries a to-do list under any heading. That one is a gate: each of those hides inside a plan that
looks finished.

Conventions are in [AGENTS.md](AGENTS.md); how to contribute is in
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
