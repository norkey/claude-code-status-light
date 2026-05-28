#!/bin/bash
# Status Light Setup Script
# Installs SwiftBar + hook + plugin for Claude Code menu bar status indicator
set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_PATH="$HOME/.claude/hooks/status_light.py"
PLUGIN_DIR="$HOME/Library/Application Support/SwiftBar/Plugins"
PLUGIN_PATH="$PLUGIN_DIR/claude-status.1s.py"
STATUS_DIR="$HOME/.claude/status"

echo "=== Status Light Setup ==="
echo ""

# Step 1: Install SwiftBar
if ! brew list --cask swiftbar &>/dev/null; then
    echo "[1/6] Installing SwiftBar..."
    brew install --cask swiftbar
else
    echo "[1/6] SwiftBar already installed ✓"
fi

# Step 2: Configure plugin directory
echo "[2/6] Configuring SwiftBar plugin directory..."
mkdir -p "$PLUGIN_DIR"
defaults write com.ameba.SwiftBar PluginDirectory "$PLUGIN_DIR"

# Step 3: Copy files
echo "[3/6] Installing hook and plugin..."
mkdir -p "$HOME/.claude/hooks" "$STATUS_DIR"
cp "$SKILL_DIR/scripts/status_light.py" "$HOOK_PATH"
cp "$SKILL_DIR/scripts/claude-status.1s.py" "$PLUGIN_PATH"
chmod +x "$HOOK_PATH" "$PLUGIN_PATH"

# Step 4: Patch settings.json
echo "[4/6] Registering hooks in settings.json..."
python3 << 'PYTHON'
import json
import os

settings_path = os.path.expanduser("~/.claude/settings.json")
hook_cmd = os.path.expanduser("~/.claude/hooks/status_light.py")

# Read existing settings
if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
else:
    settings = {}

hooks = settings.setdefault("hooks", {})

# Hook entry template
hook_entry = {"hooks": [{"type": "command", "command": hook_cmd, "timeout": 2}]}

# Events to register
events = [
    "SessionStart", "UserPromptSubmit", "PermissionRequest",
    "PreToolUse", "PostToolUse", "Notification", "Stop", "SessionEnd"
]

for event in events:
    event_hooks = hooks.setdefault(event, [])
    # Check if already registered
    already = any(
        hook_cmd in str(h)
        for h in event_hooks
    )
    if not already:
        event_hooks.append(hook_entry)

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print("    Hooks registered for:", ", ".join(events))
PYTHON

# Step 5: Add status/ to .gitignore
echo "[5/6] Updating .gitignore..."
if [ -f "$HOME/.claude/.gitignore" ]; then
    grep -q "^status/" "$HOME/.claude/.gitignore" || echo "status/" >> "$HOME/.claude/.gitignore"
else
    echo "status/" > "$HOME/.claude/.gitignore"
fi

# Step 6: Launch SwiftBar
echo "[6/6] Launching SwiftBar..."
open -a SwiftBar

echo ""
echo "=== Setup Complete ==="
echo ""
echo "You should now see a status indicator in your menu bar."
echo "  🟡 = LLM generating / tools running"
echo "  🟢 = Turn complete, waiting for input"
echo "  🔴 = Needs authorization"
echo ""
echo "The indicator will activate on your next Claude Code interaction."
