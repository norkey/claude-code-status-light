# Status Light — macOS Menu Bar Indicator for Claude Code

Real-time status indicator showing all active Claude Code sessions in your macOS menu bar.

```
Menu bar: 🟡D🟢I🔴P
```

## Colors

| Color | Meaning |
|-------|---------|
| 🟡 Yellow | LLM generating / tools running |
| 🟢 Green | Turn complete, waiting for input |
| 🔴 Red | Permission prompt, needs authorization |
| Gone | Session exited |

## Install

Ask your Claude Code agent:

> 帮我安装 status light

Or run manually:

```bash
bash ~/.claude/skills/status-light/scripts/setup.sh
```

## Requirements

- macOS
- Homebrew
- Python 3
- Claude Code 2.1+ (needs UserPromptSubmit, PermissionRequest hooks)

## How it works

1. Claude Code hooks write session status to `~/.claude/status/{session_id}.json`
2. SwiftBar plugin (1s polling) reads all status files and renders colored dots
3. Session titles are extracted from transcript `.jsonl` files (`ai-title` entries)
4. Process liveness check via `~/.claude/sessions/*.json` ensures dots persist even when idle

## Files

| File | Location |
|------|----------|
| Hook script | `~/.claude/hooks/status_light.py` |
| SwiftBar plugin | `~/Library/Application Support/SwiftBar/Plugins/claude-status.1s.py` |
| Status data | `~/.claude/status/*.json` (runtime, gitignored) |
