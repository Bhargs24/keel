---
description: Open the project progress board
---

Start the board and open it in the browser. Do not tell the user to run it.

```
python tools/board.py
```

Run it in the background so the session stays usable, and tell them the URL
(`http://127.0.0.1:7777`) in one line. If port 7777 is taken, use `--port 7778`.

Then, without being asked, print the current state as text as well, so they
have it even without switching windows:

```
python tools/track.py status
python tools/track.py next
```
