# Business & Career Skills

Six Agent Skills for business and career work: work out which direction to take, research a
company, judge whether you fit a role, prepare for the interview, get the money right, and plan how
to learn what a goal demands. Honest rather than encouraging — they are written to tell someone a
stretch is a stretch.

Each skill is a `SKILL.md` with frontmatter plus the files it needs, following the
[Agent Skills open standard](https://agentskills.io).

## The skills

| Skill | Does | Bundles |
| :--- | :--- | :--- |
| [`career-direction`](skills/careers/career-direction/) | Where to point a career when no particular job is on the table: what someone is actually selling, which role families buy it, and what that is worth in three to five years. Produces a single-file visual report. | `scripts/report_check.py`, `assets/direction-report.html` |
| [`company-research`](skills/business/company-research/) | What a company really does, how healthy it is, who it competes with, what staff say. Produces a plain-language dossier. | — |
| [`role-fit`](skills/careers/role-fit/) | Compares a background against a specific job: a verdict, a rough probability, the gaps, and the unusual strength other applicants lack. | — |
| [`pay-check`](skills/careers/pay-check/) | Local market rate for role, level and contract type; employment-versus-contracting conversion; how to reopen a number already given. | `scripts/rate_calc.py`, `rates-example.json` |
| [`interview-prep`](skills/careers/interview-prep/) | Preparation at any stage, a one-to-two page brief to read beforehand, and a page for notes during the call. Calls `company-research`, `role-fit` and `pay-check` by name when they are installed, and works alone when they are not. | `scripts/plain_check.py`, `interview-record.html` |
| [`learning-path`](skills/learning/learning-path/) | A learning path to a defined goal in any field — a language, an instrument, a sport, an exam, a job skill — built from dated research that every milestone cites. Tests the goal first, sets the hours against the evidence, and returns no path rather than a guessed one. | `scripts/path_check.py` |

Invoke one by name, or describe the task and let the agent choose.

`career-direction`, `pay-check`, `interview-prep` and `learning-path` carry a `compatibility` line
in their frontmatter: their bundled scripts need code execution, and each says what to do instead
where there is none.

## Install

Copy a skill's directory — `SKILL.md` and everything beside it — into wherever the agent reads
skills from. Packaged `.skill` archives for all six are attached to the `latest` release, which
CI rebuilds from `master` on every push.

## Layout

```
skills/
├── business/
│   └── company-research/
├── careers/
│   ├── career-direction/
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

`skills/careers/career-direction/scripts/report_check.py` reads a filled direction report and
fails on what makes one worthless or unsafe to forward; `--help` lists it. That one is a gate,
because most of those defects are invisible: a mistyped key draws an empty cell and says nothing,
so the report still looks finished. Its privacy check reads common shapes and can flag something
harmless, such as an order number that reads as a phone number; the message names the field, and
rewording it clears the flag. Its cases, and the page's, run with
`python3 -I skills/careers/career-direction/evals/test_report.py`. The ones that render the
page need Playwright and a Chromium, and are skipped without them.

`skills/learning/learning-path/scripts/path_check.py` reads a drafted learning plan and fails on
the defects `--help` lists. `--help` also says what the script cannot check.

Conventions are in [AGENTS.md](AGENTS.md); how to contribute is in
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
