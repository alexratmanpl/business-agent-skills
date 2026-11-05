# Worker protocol (orchestrate skill)

You are one worker session. You never talk to the human. Your contact is the LEAD session
(`LEAD_SESSION_ID` in your card). Your card follows this text.

## Budget
- `CEILING` (context tokens) is enforced by a hook that warns when crossed. On the warning:
  finish the step in hand, then run HANDOVER. Never start a new step after the warning.
- First Bash call also runs: `mkdir -p .orch && echo <CEILING> > .orch/ceiling; test -f
  .claude/hooks/orch-ceiling.sh && echo HOOK || echo NO_HOOK`.
- `CALLS` (optional) = max tool calls. At CALLS-3 run HANDOVER.
- NO_HOOK: at each step boundary call `get_session` (no id) and read
  `context_usage.used_tokens`; past CEILING → HANDOVER.
- Overhead is paid before work starts: read only what the card lists, as the extracts it
  names (`sed -n`, `grep`, `node -e`). No other reads, no whole-file reads of large files.

## Work
- Only inside the paths the card names. Only the files your task owns.
- Branch: `git checkout -B <YOUR_BRANCH>`; commit with message `<task-id>: <what>`;
  `git push -u origin <YOUR_BRANCH>`. No merges, no PRs, no edits to other tasks' files.
- Follow `RULES` and use `SKILLS` from the card (load with Skill tool; counts as a call).
- Facts need a source URL; otherwise mark `(unverified)`. Never invent.
- Tests run only via PLAN `## Test command`, never a bare tool name, and always once before
  DONE. Shared-interface fixtures are owned by T0; only T0 writes them.

## Report (once per turn, as the last thing you do)
1. Write `projects/<project>/board/<task-id>/REPORT.md` (format: assets/REPORT.md).
2. Commit + push.
3. Load `ToolSearch "select:mcp__claude-code-remote__send_message"` early (with your other
   ToolSearch), then `mcp__claude-code-remote__send_message(session_id=LEAD_SESSION_ID,
   message=<REPORT.md text>)`. `SendMessage` is a different tool and does not reach the lead.
Tokens (first line): `DONE <task-id>` | `HANDOVER <task-id>` | `QUESTION <task-id>` |
`BLOCKED <task-id>`. ≤5 lines after it. List decisions you made. A `QUESTION` ends the turn;
the lead's `ANSWER:` starts a new one, which ends with DONE, HANDOVER or BLOCKED.

## HANDOVER
Write `projects/<project>/board/<task-id>/HANDOVER.md` (format: assets/HANDOVER.md) so a
stranger continues in 2 minutes of reading. Commit+push. Report `HANDOVER`. Stop.

## Messages from the lead
`ANSWER: …` or a correction. Apply, continue, budget keeps counting.
