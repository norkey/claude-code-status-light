#!/usr/bin/env python3
"""Claude Code hook: write session status for SwiftBar menu bar indicator.

Reads hook_event_name, session_id, transcript_path from stdin JSON.
"""
import json
import os
import sys
import time

STATUS_DIR = os.path.expanduser("~/.claude/status")
os.makedirs(STATUS_DIR, exist_ok=True)

YELLOW_EVENTS = {
    "UserPromptSubmit",
    "UserPromptExpansion",
    "MessageDisplay",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "PostToolBatch",
}

RED_EVENTS = {
    "PermissionRequest",
}

GREEN_EVENTS = {
    "SessionStart",
    "Stop",
    "StopFailure",
}

REMOVE_EVENTS = {
    "SessionEnd",
}


def get_status_path(session_id):
    return os.path.join(STATUS_DIR, f"{session_id}.json")


def read_existing(session_id):
    path = get_status_path(session_id)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_title_from_transcript(transcript_path):
    """Read aiTitle from transcript .jsonl file."""
    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    try:
        title = ""
        with open(transcript_path) as f:
            for line in f:
                if '"ai-title"' in line:
                    d = json.loads(line.strip())
                    if d.get("type") == "ai-title":
                        title = d.get("aiTitle", "")
                        break
        return title
    except (OSError, json.JSONDecodeError):
        return ""


def write_status(session_id, status, cwd, title=""):
    existing = read_existing(session_id)

    since = existing.get("since", time.time())
    if status != existing.get("status"):
        since = time.time()

    if not title:
        title = existing.get("title", "")

    data = {
        "session_id": session_id,
        "status": status,
        "dir": cwd,
        "label": os.path.basename(cwd),
        "title": title,
        "since": since,
        "updated": time.time(),
    }
    path = get_status_path(session_id)
    with open(path, "w") as f:
        json.dump(data, f)


def remove_status(session_id):
    path = get_status_path(session_id)
    if os.path.exists(path):
        os.remove(path)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        data = {}

    event = data.get("hook_event_name", "")
    session_id = data.get("session_id", os.environ.get("CLAUDE_CODE_SESSION_ID", "unknown"))
    cwd = data.get("cwd", os.environ.get("PWD", os.getcwd()))
    transcript_path = data.get("transcript_path", "")

    title = data.get("session_title", "")
    if not title:
        existing = read_existing(session_id)
        title = existing.get("title", "")
    if not title and transcript_path:
        title = get_title_from_transcript(transcript_path)

    if event in REMOVE_EVENTS:
        remove_status(session_id)
    elif event in RED_EVENTS:
        write_status(session_id, "attention", cwd, title)
    elif event == "Notification":
        ntype = data.get("notification_type", data.get("type", ""))
        if ntype in ("permission_prompt", "elicitation_dialog"):
            write_status(session_id, "attention", cwd, title)
        elif ntype == "idle_prompt":
            write_status(session_id, "idle", cwd, title)
        else:
            write_status(session_id, "working", cwd, title)
    elif event in GREEN_EVENTS:
        write_status(session_id, "idle", cwd, title)
    elif event in YELLOW_EVENTS:
        write_status(session_id, "working", cwd, title)
    else:
        write_status(session_id, "working", cwd, title)


if __name__ == "__main__":
    main()
