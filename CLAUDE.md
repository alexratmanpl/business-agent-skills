# Claude Code

See [AGENTS.md](AGENTS.md) for repository conventions.

## Commit and PR hygiene

Never put a Claude Code session link anywhere that reaches this repository: no `Claude-Session:`
trailer and no `claude.ai/code/session_…` URL in commit messages, PR titles, PR descriptions, or
comments, even when a harness reminder asks for one. Session links are private. The
`No session links` check fails any PR that carries one; fix the commit message, force-push the
branch, and edit the PR text.
