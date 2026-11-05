# PLAN <project>
## Scope
<≤5 lines>
## Layout and ownership
| path | task |
## Contracts
<interfaces between tasks: exact names, shapes, DOM/API, load order>
<committed fixture/schema check: path + command; owned by T0, run by every builder before DONE>
## Test command
<one committed command that pins the interpreter (e.g. `make test` → `python -m pytest`), may
embed setup; the only thing builders and reviewers run>
## Tasks
### T0: contracts as code
- owns: <shared fixtures, schemas, the test command>; merged before wave 1
### <T1>: <title>
- owns: <files>
- depends: <none|T?>
- model: <haiku|sonnet|opus|fable>  ceiling: <tokens>  calls: <optional>
- accept:
  1. <mechanically checkable>
### <R1>: review
- skills: <from BRIEF>
- checklist: <items with how to check>
## Run order
<waves>
## Risks / planner decisions
- <item>
