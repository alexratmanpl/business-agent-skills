# <project>
## Goal
<1-3 lines: the deliverable>
## Done when
- <checkable acceptance criterion>
## Constraints
- stack / no-gos / must open-run how
- rules file: <AGENTS.md|CLAUDE.md path>  (workers obey it)
- network hosts needed: <host list or none>   (lead tests each before the first spawn)
## Inputs
- <path or URL>
## Unspecified
- <thing agents must research or decide>   (suffix `(ask)` = human must decide)
## Risk
<blank: the lead scores it>   one point each, ≥3 = high:
- irreversible: prod data, money, auth/security, legal or published text, migrations
- blast radius: more than one module or consumer depends on the result
- ambiguity: ≥3 Unspecified items, or any `(ask)`
- coupling: ≥2 build tasks share an interface the planner must invent
- verifiability: acceptance cannot be checked mechanically
- novelty: unfamiliar stack, rules file >1 page, or external APIs without docs in the repo
## Skills
- builder: <skill names>
- reviewer: <skill names>   (mandatory; every skill named here must exist in this repo:
  `.claude/skills/<name>/` or `enabledPlugins` in `.claude/settings.json`; workers are fresh
  clones and see no user-level plugins)
## Models
<optional per-role overrides of references/spawn.md>
## Keep sessions
<yes to skip archiving finished worker sessions at CLOSE; default no>
