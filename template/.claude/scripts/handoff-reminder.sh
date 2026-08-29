#!/bin/sh
# Stop hook. Checks the ceremony actually happened, rather than hoping.
cd "$(dirname "$0")/../.." || exit 0

WARN=""

if [ -d tracker/tasks ]; then
  TODAY=$(date +%Y-%m-%d)
  STALE=$(grep -l '^status: doing' tracker/tasks/*.md 2>/dev/null | while read -r f; do
            grep -q "^- $TODAY" "$f" || basename "$f" .md
          done | tr '\n' ' ')
  [ -n "$STALE" ] && WARN="$WARN
  IN FLIGHT WITH NO ENTRY TODAY: $STALE
    Run: python tools/track.py log <ID> \"what happened\"
    Do it now, yourself. Do not ask the developer to."
fi

if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  WARN="$WARN
  UNCOMMITTED CHANGES. Commit them, or say plainly what is left and why."
fi

LATEST=$(ls -t docs/40-HANDOFF/*.md 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
  case "$(basename "$LATEST")" in
    "$(date +%Y-%m-%d)"*) ;;
    *) WARN="$WARN
  NO HANDOFF TODAY. Write docs/40-HANDOFF/$(date +%Y-%m-%d)-<slug>.md:
    what is done, what is half-done, the next action, and what you know
    that is not written anywhere. Write it yourself." ;;
  esac
fi

if [ -n "$WARN" ]; then
  echo "════════ BEFORE YOU STOP ════════"
  echo "$WARN"
  echo "═════════════════════════════════"
fi
exit 0
