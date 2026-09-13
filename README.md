# Business & Career Skills

Four Agent Skills for business and career work: research a company, judge whether you fit a role,
prepare for the interview, and get the money right. Honest rather than encouraging — they are
written to tell someone a stretch is a stretch.

Each skill is a `SKILL.md` with frontmatter plus the files it needs, following the
[Agent Skills open standard](https://agentskills.io).

## The skills

| Skill | Does | Bundles |
| :--- | :--- | :--- |
| [`company-research`](skills/business/company-research/) | What a company really does, how healthy it is, who it competes with, what staff say. Produces a plain-language dossier. | — |
| [`role-fit`](skills/careers/role-fit/) | Compares a background against a specific job: a verdict, a rough probability, the gaps, and the unusual strength other applicants lack. | — |
| [`pay-check`](skills/careers/pay-check/) | Local market rate for role, level and contract type; employment-versus-contracting conversion; how to reopen a number already given. | `scripts/rate_calc.py`, `rates-example.json` |
| [`interview-prep`](skills/careers/interview-prep/) | Preparation at any stage, a one-to-two page brief to read beforehand, and a page for notes during the call. Calls the other three by name when they are installed, and works alone when they are not. | `scripts/plain_check.py`, `interview-record.html` |

Invoke one by name, or describe the task and let the agent choose.

`pay-check` and `interview-prep` carry a `compatibility` line in their frontmatter: their bundled
scripts need code execution, and each says what to do instead where there is none.

## Install

This repository is also a Claude Code plugin marketplace. `.claude-plugin/marketplace.json`
declares the marketplace as `alexratmanpl` and one plugin, `business-agent-skills`:

```
/plugin marketplace add alexratmanpl/business-agent-skills
/plugin install business-agent-skills@alexratmanpl
```

For a single skill, copy its directory — `SKILL.md` and everything beside it — into wherever the
agent reads skills from. Packaged `.skill` archives for all four are attached to the `latest`
release, which CI rebuilds from `master` on every push.

## Layout

```
skills/
├── business/
│   └── company-research/
└── careers/
    ├── role-fit/
    ├── pay-check/
    └── interview-prep/
```

Categories organise this repository only. Installing flattens them, so skill names must be unique
across all categories.

## Development

`python3 scripts/build_skills.py --check-only` validates every skill: frontmatter parses and has a
name and description, the name matches the directory that gets installed, every bundled file the
body points at exists, and the body is not still a placeholder. Drop `--check-only` to write
`.skill` archives to `dist/`. CI runs it on every pull request.

`skills/careers/interview-prep/scripts/plain_check.py` reads a drafted brief — or the skill's own
prose — for long sentences, abbreviations used before being spelled out, machine phrasing and
excess length. It reports and exits zero; it is a checklist, not a gate.

Conventions are in [AGENTS.md](AGENTS.md); how to contribute is in
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
