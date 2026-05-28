---
name: status-light
description: macOS 菜单栏状态灯。实时显示所有 Claude Code session 的运行状态（🟡生成中 🟢完成 🔴需授权），多 session 并排显示对话首字母。触发词：status light, 状态灯, 安装状态灯, setup status light, 菜单栏指示灯
---

# Status Light — macOS 菜单栏 Claude Code 状态灯

在 macOS 菜单栏实时显示所有 Claude Code session 的运行状态，一眼看出哪个窗口在跑、哪个等你操作。

## 效果

```
菜单栏：🟡D🟢I🔴P
下拉：
  🟡 Discuss traffic light — working (2m)
  🟢 Install SillyTavern — idle (5m)
  🔴 Plan AI roleplay — attention (<1m)
```

## 颜色语义

| 颜色 | 含义 | 触发事件 |
|------|------|---------|
| 🟡 黄 | LLM 生成中 / 工具执行中 | UserPromptSubmit, PreToolUse, PostToolUse |
| 🟢 绿 | 本轮完成，等待用户输入 | Stop, SessionStart（刚打开还没发消息） |
| 🔴 红 | 需要用户授权 | PermissionRequest, Notification(permission_prompt) |
| 消失 | session 已退出 | SessionEnd / 进程死亡 |

## 安装

用户说"安装状态灯"或"setup status light"时，执行以下步骤：

### Step 1: 安装 SwiftBar

```bash
brew install --cask swiftbar
```

如果已安装则跳过。

### Step 2: 配置 SwiftBar 插件目录

```bash
defaults write com.ameba.SwiftBar PluginDirectory "$HOME/Library/Application Support/SwiftBar/Plugins"
mkdir -p "$HOME/Library/Application Support/SwiftBar/Plugins"
```

### Step 3: 复制文件

将以下文件复制到对应位置：

1. `scripts/status_light.py` → `~/.claude/hooks/status_light.py`（chmod +x）
2. `scripts/claude-status.1s.py` → `~/Library/Application Support/SwiftBar/Plugins/claude-status.1s.py`（chmod +x）
3. 创建 `~/.claude/status/` 目录

### Step 4: 注册 Hooks

在用户的 `~/.claude/settings.json` 的 `hooks` 字段中追加以下事件（不要覆盖已有 hooks）：

需要注册的事件：
- `SessionStart`
- `UserPromptSubmit`
- `PermissionRequest`
- `PreToolUse`
- `PostToolUse`
- `Notification`
- `Stop`
- `SessionEnd`

每个事件的 hook 格式相同：
```json
{
  "hooks": [
    {
      "type": "command",
      "command": "~/.claude/hooks/status_light.py 的绝对路径",
      "timeout": 2
    }
  ]
}
```

**注意**：`command` 字段必须用绝对路径（如 `/Users/username/.claude/hooks/status_light.py`），不能用 `~`。

### Step 5: 启动 SwiftBar

```bash
open -a SwiftBar
```

### Step 6: 验证

```bash
echo '{"hook_event_name":"UserPromptSubmit","session_id":"test","cwd":"'$HOME'"}' | python3 ~/.claude/hooks/status_light.py
python3 ~/Library/Application\ Support/SwiftBar/Plugins/claude-status.1s.py
rm ~/.claude/status/test.json
```

应该能看到输出带有 🟡 圆点。

## 技术要点

- Hook 通过 **stdin JSON** 获取 `hook_event_name`、`session_id`、`transcript_path`（官方协议）
- Session 标题从 transcript `.jsonl` 文件中的 `ai-title` 条目提取
- 进程存活检测：读取 `~/.claude/sessions/*.json` 的 PID，`os.kill(pid, 0)` 判活
- 过期清理仅针对进程已死的 session（working 2min / idle 30min / attention 10min）

## 前置要求

- macOS（SwiftBar 仅支持 macOS）
- Homebrew
- Python 3
- Claude Code 2.1+（需要支持 UserPromptSubmit、PermissionRequest hook 事件）

## 注意事项

- **Hook 脚本的参数必须有默认值**：PreToolUse hook 崩溃会瘫痪所有工具调用，LLM 无法自修复
- **改完 hook 脚本后清 `__pycache__`**：Python 字节码缓存可能用旧版本
- SwiftBar 每 1 秒轮询一次，延迟 <1s
- `.claude/status/` 目录应加入 `.gitignore`
