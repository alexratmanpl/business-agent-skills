#!/usr/bin/env bash
# Fail if a Claude Code session link appears in any commit message, any added diff line,
# or the PR title/body between BASE_REF and HEAD_REF.
#
# CI:    .github/workflows/no-session-links.yml sets BASE_REF, HEAD_REF, PR_TITLE, PR_BODY.
# Local: BASE_REF=origin/master HEAD_REF=HEAD scripts/check_no_session_links.sh
set -euo pipefail

BASE_REF="${BASE_REF:-origin/master}"
HEAD_REF="${HEAD_REF:-HEAD}"
# Requires a real id so prose that merely names the format (docs, this script) does not trip it.
PATTERN='claude\.ai/code/session_[A-Za-z0-9]+|session_[A-Za-z0-9]{20,}'
status=0

range="$(git merge-base "$BASE_REF" "$HEAD_REF")..$HEAD_REF"

echo "Scanning commit messages in $range"
while read -r sha; do
  [ -z "$sha" ] && continue
  if hits=$(git log -1 --format=%B "$sha" | grep -nE "$PATTERN"); then
    echo "::error::commit $(git log -1 --format='%h %s' "$sha") contains a session link"
    printf '%s\n' "$hits" | sed 's/^/    /'
    status=1
  fi
done < <(git rev-list "$range")

echo "Scanning added lines in the diff"
if hits=$(git diff "$range" | grep -E '^\+[^+]' | grep -nE "$PATTERN"); then
  echo "::error::the diff adds a session link"
  printf '%s\n' "$hits" | sed 's/^/    /'
  status=1
fi

if [ -n "${PR_TITLE:-}${PR_BODY:-}" ]; then
  echo "Scanning PR title and body"
  if hits=$(printf '%s\n%s\n' "${PR_TITLE:-}" "${PR_BODY:-}" | grep -nE "$PATTERN"); then
    echo "::error::the PR title or description contains a session link"
    printf '%s\n' "$hits" | sed 's/^/    /'
    status=1
  fi
fi

if [ "$status" -ne 0 ]; then
  cat <<'MSG'

Session links are private and must not reach this repository.
Fix: delete the line from each flagged commit message (amend or rebase), force-push the
branch, and edit the PR description. See CLAUDE.md, "Commit and PR hygiene".
MSG
  exit 1
fi

echo "OK: no session links found"
