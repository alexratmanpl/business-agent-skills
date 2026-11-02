#!/usr/bin/env bash
# orchestrate skill: warn when this session's context passes its ceiling, so the agent hands off
# at the next boundary. Ceiling: .orch/ceiling in cwd > $ORCH_CEILING > 100000. Repeats every STEP.
set -u
STEP="${ORCH_STEP:-20000}"
command -v jq >/dev/null 2>&1 || exit 0
input="$(cat)"
[ -z "$(jq -r '.agent_id // empty' <<<"$input")" ] || exit 0   # subagents: main session acts
path="$(jq -r '.transcript_path // empty' <<<"$input")"
event="$(jq -r '.hook_event_name // empty' <<<"$input")"
sid="$(jq -r '.session_id // "na"' <<<"$input")"
cwd="$(jq -r '.cwd // empty' <<<"$input")"
[ -n "$path" ] && [ -f "$path" ] || exit 0
CEILING="${ORCH_CEILING:-100000}"
if [ -n "$cwd" ] && [ -f "$cwd/.orch/ceiling" ]; then
  c="$(tr -dc 0-9 <"$cwd/.orch/ceiling")"; [ -n "$c" ] && CEILING="$c"
fi
case "$CEILING" in ''|*[!0-9]*) CEILING=100000;; esac
ctx="$({ tac "$path" 2>/dev/null || tail -r "$path" 2>/dev/null; } | grep -m 50 '"type":"assistant"' \
  | jq -rR 'fromjson? // empty | .message.usage | select(. != null)
            | (if (.iterations | type) == "array"
               then ([.iterations[] | select(.type == "message")] | last) // . else . end)
            | ((.input_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0))' 2>/dev/null \
  | sort -n | tail -n 1)"   # max over the newest entries: partial stream rows under-read
[ -n "$ctx" ] || exit 0
mark="${TMPDIR:-/tmp}/orch-ceiling-${sid}"
if [ "$ctx" -le "$CEILING" ] 2>/dev/null; then rm -f "$mark"; exit 0; fi   # non-numeric ctx → warn
last=0; [ -f "$mark" ] && last="$(cat "$mark" 2>/dev/null || echo 0)"
[ $((ctx - last)) -ge "$STEP" ] || exit 0
printf '%s' "$ctx" >"$mark"
msg="Context is at $((ctx / 1000))k tokens, past the $((CEILING / 1000))k ceiling. Finish the step in hand, then HANDOVER (worker) or lead succession (lead) per the orchestrate skill."
if [ "$event" = "UserPromptSubmit" ]; then printf '%s\n' "$msg"
else jq -cn --arg e "$event" --arg m "$msg" '{hookSpecificOutput:{hookEventName:$e,additionalContext:$m}}'; fi
exit 0
