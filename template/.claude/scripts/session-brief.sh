#!/bin/sh
# SessionStart. Loads the state so nobody has to know a command exists.
# Claude reads this and acts on it; the developer never has to ask.
cd "$(dirname "$0")/../.." || exit 0

echo "════════ SESSION BRIEF ════════"
echo
echo "You are the operator. Run the tools yourself. Never ask the developer to"
echo "run a command you can run. Never ask them to open the board or the tracker."
echo

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
echo "── branch ──"
echo "  $BRANCH"
case "$BRANCH" in
  */*) ;;   # <person>/<TASK-ID>-<slug>
  main) echo "  ON MAIN. Work goes on a branch: <person>/<TASK-ID>-<slug>."
        echo "  Create it yourself before the first edit. Never push to main." ;;
  *)    echo "  This branch declares no owner, so the ownership check will refuse it."
        echo "  Rename it to <person>/<TASK-ID>-<slug> yourself." ;;
esac

if [ -f docs/10-STATUS/NOW.md ]; then
  echo
  echo "── claimed right now (docs/10-STATUS/NOW.md) ──"
  sed -n '/^## Claims/,/^## /p' docs/10-STATUS/NOW.md | grep '^|' | head -8 | sed 's/^/  /'
fi

if [ -d tracker/tasks ]; then
  echo
  echo "── tracker ──"
  python tools/track.py status 2>/dev/null | head -6 | sed 's/^/  /'
  echo
  echo "── ready to start ──"
  python tools/track.py next 2>/dev/null | sed -n '3,9p' | sed 's/^/  /'
  echo
  echo "── waiting on the other person ──"
  python tools/track.py blocked 2>/dev/null | sed -n '2,10p' | sed 's/^/  /'
  echo
  echo "  Board: python tools/board.py   (open it for them, do not tell them to)"
fi

if [ -d spec ] && [ -z "$(ls -A spec 2>/dev/null)" ]; then
  echo
  echo "  spec/ IS EMPTY. Run `make spec` yourself before reading any spec."
fi

echo
echo "First move: read docs/00-RULES/THE-RULEBOOK.md. It is the one book."
echo "═════════════════════════════════════"
