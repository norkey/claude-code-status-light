# Status Light — macOS Menu Bar Indicator for Claude Code

Real-time status indicator showing all active Claude Code sessions in your macOS menu bar.

在 macOS 菜单栏实时显示所有 Claude Code session 的运行状态。

```
Menu bar: 🟡D🟢I🔴P
```

## Colors / 颜色语义

| Color | Meaning | 含义 |
|-------|---------|------|
| 🟡 Yellow | LLM generating / tools running | LLM 生成中 / 工具执行中 |
| 🟢 Green | Turn complete, waiting for input | 本轮完成，等待用户输入 |
| 🔴 Red | Permission prompt, needs authorization | 需要用户授权 |
| Gone | Session exited | Session 已退出 |

## Install / 安装

Ask your Claude Code agent:

> 帮我安装 status light

Or run manually / 或手动执行：

```bash
git clone https://github.com/norkey/claude-code-status-light ~/.claude/skills/status-light
bash ~/.claude/skills/status-light/scripts/setup.sh
```

## Requirements / 前置要求

- macOS
- Homebrew
- Python 3
- Claude Code 2.1+（需要支持 UserPromptSubmit、PermissionRequest hook 事件）

## How it works / 工作原理

1. Claude Code hooks write session status to `~/.claude/status/{session_id}.json`
   — Hook 监听 Claude Code 生命周期事件，将状态写入 JSON 文件
2. SwiftBar plugin (1s polling) reads all status files and renders colored dots
   — SwiftBar 插件每秒读取状态文件，渲染菜单栏圆点
3. Session titles are extracted from transcript `.jsonl` files (`ai-title` entries)
   — 对话标题从 transcript 文件中提取
4. Process liveness check via `~/.claude/sessions/*.json` ensures dots persist even when idle
   — 通过进程存活检测确保 idle 状态的点不会消失

## Files / 文件说明

| File | Location | 说明 |
|------|----------|------|
| Hook script | `~/.claude/hooks/status_light.py` | 状态写入脚本 |
| SwiftBar plugin | `~/Library/Application Support/SwiftBar/Plugins/claude-status.1s.py` | 菜单栏渲染 |
| Status data | `~/.claude/status/*.json` | 运行时数据（gitignored） |

## License

MIT
