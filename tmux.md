# Persistent Jupyter Notebook on serima-gpu — Setup & Fix Log

**Server:** `serima-gpu` (Ubuntu 24.04.4 LTS)
**User:** `serima`
**Project path:** `~/Sanjidh090`
**Date resolved:** 2026-06-26

---

## Problem

Notebooks (and tmux sessions in general) were dying after fully disconnecting from VS Code Remote-SSH, even though `tmux` was already being used to "protect" the Jupyter server. Reconnecting later showed the kernel stopped or restarted, despite tmux normally surviving terminal closures.

## Root Cause

```bash
loginctl show-user serima | grep Linger
```
returned `Linger=no`.

By default, when all SSH sessions for a user end, `systemd-logind` tears down **everything** tied to that user — including tmux sessions — because the system sees "zero active logins" as a signal to clean up. tmux protects against the *terminal* closing (SIGHUP), but not against the *entire user session* being killed by the OS. Linger is the setting that tells systemd to keep a user's processes alive even with no active login sessions.

## Fix

Enable linger for the user:

```bash
sudo loginctl enable-linger serima
```

Verify:

```bash
loginctl show-user serima | grep Linger
# Linger=yes
```

This is a one-time fix — it persists across reboots once set.

---

## Verified Setup: Persistent Jupyter via tmux

### 1. Start a tmux session for the Jupyter server

```bash
tmux new -s jupyter
cd ~/Sanjidh090
source venv/bin/activate
jupyter lab --no-browser --port=8888
```

Copy the printed URL, e.g.:
```
http://localhost:8888/?token=xxxxxxxx
```

Detach (don't close the terminal):
```
Ctrl+b, then d
```

### 2. Connect VS Code to the existing server

Newer VS Code Jupyter extension versions removed the old `Jupyter: Specify Jupyter Server for Connections` command. Use this path instead:

1. Open the notebook.
2. Click the kernel picker (top-right of the notebook).
3. Choose **"Select Another Kernel..."**
4. Choose **"Existing Jupyter Server..."**
5. Paste the `http://localhost:8888/?token=...` URL.
6. Give the server a label (e.g. `persistent-tmux`).
7. From the kernel list, select the venv-based kernel pointing to `Sanjidh090/venv/bin/python3` (may appear as `Python (venv)` or a custom-named kernel — both are equivalent if they point to the same interpreter path).

### 3. Confirm the connection is real (not a local fallback kernel)

Run in a notebook cell:
```python
import os
print(os.getpid())
```

In a **separate terminal**, attach to the server's tmux session and confirm the Jupyter server logs show the kernel connecting:
```bash
tmux attach -t jupyter
```
Seeing `Connecting to kernel ...` in the tmux pane at the same time confirms VS Code is using the persistent external server, not its own internal one.

---

## End-to-End Persistence Test (passed)

1. Ran in a notebook cell:
```python
import time
from datetime import datetime
i = 0
while True:
    print(f"[{i}] Still alive: {datetime.now()}", flush=True)
    i += 1
    time.sleep(5)
```
2. Fully closed VS Code / disconnected SSH.
3. Waited several minutes.
4. Reopened VS Code, reconnected Remote-SSH, reopened the notebook.
5. Reconnected to the same kernel via **Existing Jupyter Server** → same URL → same venv kernel.
6. **Result:** counter continued incrementing from where it left off (no restart to `[0]`, no idle/stopped cell). Confirmed via tmux logs and live output in the notebook.

---

## Cleaning Up Stray tmux Sessions

If `tmux ls` shows an unnamed session (e.g. `0: 1 windows ...`) with nothing obviously running in it, it's likely just an idle shell from a session created without `-s name`. To reset everything and start clean:

**1. Kill all tmux sessions at once:**
```bash
tmux kill-server
```

**2. Confirm nothing's left:**
```bash
tmux ls
# should say "no server running on ..."
```

**3. Check for orphaned Jupyter processes** (these can survive outside tmux thanks to linger, even after `tmux kill-server`):
```bash
ps aux | grep jupyter
```
If one is listed, kill it by PID:
```bash
kill <PID>
```

**4. Start a fresh, properly named session:**
```bash
tmux new -s jupyter
cd ~/Sanjidh090
source venv/bin/activate
jupyter lab --no-browser --port=8888
```
Copy the new URL, detach with `Ctrl+b` then `d`, then reconnect VS Code via **Existing Jupyter Server** as described above.

> Tip: always use `tmux new -s <name>` instead of `tmux new` so sessions don't end up as anonymous numbers like `0`.

---

## Notes for Future Long Runs

- Always check `os.getpid()` before starting multi-day training — if the PID changes after a reconnect, VS Code silently fell back to an internal kernel and you need to redo the "Existing Jupyter Server" step.
- Keep saving checkpoints regardless of persistence setup:
```python
torch.save({
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "epoch": epoch,
}, f"checkpoint_epoch_{epoch}.pt")
```
- Linger only needed to be enabled once; it survives reboots.
- Don't run `tmux kill-session -t jupyter` unless you intend to kill all active kernels.
