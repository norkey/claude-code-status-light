#!/usr/bin/env python3
"""SwiftBar plugin: Claude Code session status indicator (multi-dot)."""
import json
import os
import time

STATUS_DIR = os.path.expanduser("~/.claude/status")
STALE_SECONDS = {
    "working": 3600,    # 1 hour — process-alive check is the real guard
    "idle": 3600,       # 1 hour
    "attention": 3600,  # 1 hour
}

COLORS = {
    "idle": "#34C759",       # green
    "working": "#FF9500",    # yellow/orange
    "attention": "#FF3B30",  # red
}

PRIORITY = {"attention": 0, "working": 1, "idle": 2}


SESSIONS_DIR = os.path.expanduser("~/.claude/sessions")


def is_process_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def get_alive_session_ids():
    """Read ~/.claude/sessions/*.json to find actually alive sessions."""
    alive = {}
    if not os.path.isdir(SESSIONS_DIR):
        return alive
    for f in os.listdir(SESSIONS_DIR):
        if not f.endswith(".json"):
            continue
        try:
            with open(os.path.join(SESSIONS_DIR, f)) as fh:
                data = json.load(fh)
            pid = data.get("pid", 0)
            if pid and is_process_alive(pid):
                alive[data.get("sessionId", "")] = data
        except (json.JSONDecodeError, OSError):
            continue
    return alive


def load_sessions():
    sessions = []
    alive_ids = get_alive_session_ids()
    if not os.path.isdir(STATUS_DIR):
        return sessions
    now = time.time()
    for f in os.listdir(STATUS_DIR):
        if not f.endswith(".json"):
            continue
        path = os.path.join(STATUS_DIR, f)
        try:
            with open(path) as fh:
                data = json.load(fh)
            session_id = data.get("session_id", "")
            # If session process is alive, always show it
            if session_id in alive_ids:
                sessions.append(data)
                continue
            # Dead process: hide if stale, clean up if very old (>1h)
            age = now - data.get("updated", 0)
            if age > 3600:
                os.remove(path)
                continue
            status = data.get("status", "working")
            max_age = STALE_SECONDS.get(status, 3600)
            if age > max_age:
                continue  # hide but don't delete yet
            sessions.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    # Add alive sessions that have no status file yet
    seen_ids = {s.get("session_id") for s in sessions}
    for sid, sdata in alive_ids.items():
        if sid not in seen_ids:
            sessions.append({
                "session_id": sid,
                "status": "working" if sdata.get("status") == "busy" else "idle",
                "dir": sdata.get("cwd", ""),
                "label": os.path.basename(sdata.get("cwd", "")),
                "title": "",
                "since": sdata.get("startedAt", time.time() * 1000) / 1000,
                "updated": sdata.get("updatedAt", time.time() * 1000) / 1000,
            })
    sessions.sort(key=lambda s: PRIORITY.get(s.get("status", "idle"), 9))
    return sessions


def render():
    sessions = load_sessions()
    if not sessions:
        print("⚪ | size=14")
        print("---")
        print("No active Claude Code sessions")
        return

    dots = []
    for s in sessions:
        color = COLORS.get(s.get("status", "idle"), "#8E8E93")
        dots.append(f":circle.fill: | sfcolor={color} size=10")

    # Menu bar: colored dots using SF Symbols
    # SwiftBar supports inline SF symbols but simpler to use emoji-style
    bar_parts = []
    for s in sessions:
        status = s.get("status", "idle")
        # Debounce: if idle for less than 3s, still show as working (avoids flicker on internal turn boundaries)
        if status == "idle":
            since = s.get("since", 0)
            if time.time() - since < 3:
                status = "working"
        if status == "attention":
            dot = "🔴"
        elif status == "working":
            dot = "🟡"
        else:
            dot = "🟢"
        # First letter of session title, fallback to directory name
        title = s.get("title", "")
        if title:
            initial = title[0].upper()
        else:
            label = s.get("label", "")
            if not label or label.startswith("."):
                label = os.path.basename(os.path.dirname(s.get("dir", ""))) or "?"
            initial = label[0].upper() if label else "?"
        bar_parts.append(f"{dot}{initial}")

    print(f"{''.join(bar_parts)} | size=13")
    print("---")
    status_emoji = {"attention": "🔴", "working": "🟡", "idle": "🟢"}
    for s in sessions:
        status = s.get("status", "idle")
        if status == "idle" and time.time() - s.get("since", 0) < 3:
            status = "working"
        title = s.get("title", "") or s.get("label", s.get("dir", "unknown"))
        elapsed = int(time.time() - s.get("since", time.time()))
        mins = elapsed // 60
        time_str = f"{mins}m" if mins > 0 else "<1m"
        dot = status_emoji.get(status, "⚪")
        print(f"{dot} {title} — {status} ({time_str})")
    print("---")
    print("Refresh | refresh=true")


if __name__ == "__main__":
    render()
