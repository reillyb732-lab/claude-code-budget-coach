# Budget Coach Lite

**Stop hitting your Claude Code limit mid-task.** A free status line that shows your 5-hour usage *and predicts when you'll run out* at your current pace.

```
Opus 5.5 │ 5h ████······ 45% resets 1:25am │ ⚠ limit ~11:02pm at this pace · try /model sonnet │ wk 20% │ ctx 72% (/compact saves usage)
```

- **5h bar:** your real usage from Claude Code, color-coded green → yellow → red
- **Forecast:** measures your burn rate over the last 30 minutes and warns you *before* you hit the wall, with a tip on what to do
- **wk:** weekly limit used
- **ctx:** context window used (big context = expensive messages)

Works on Pro and Max plans. No account, no API key, no data leaves your computer.

## Install (2 minutes)

1. You need Python 3.8+ (`python --version`).
2. Download [`budget_coach.py`](https://raw.githubusercontent.com/reillyb732-lab/claude-code-budget-coach/main/budget_coach.py) (right-click → Save link as) and save it, for example, to `~/.claude/budget_coach.py`.
3. Add this to `~/.claude/settings.json` (create the file if it doesn't exist):

```json
{
  "statusLine": {
    "type": "command",
    "command": "python ~/.claude/budget_coach.py",
    "refreshInterval": 30
  }
}
```

On macOS/Linux use `python3` instead of `python`. On Windows, use the full path with forward slashes:

```json
"command": "python \"C:/Users/you/.claude/budget_coach.py\""
```

4. Restart Claude Code. Usage appears after your first reply; the forecast after a few minutes of work.

## Want more?

**Budget Coach Pro** adds a waste detector (catches full test-suite runs, giant file reads and bloated MCP setups as they happen), automatic model routing, a `/lean` mode and a weekly "where did my usage go" report. → *[link coming soon]*

## Also by me

**[Safe Mode](https://github.com/reillyb732-lab/claude-code-safe-mode)**: blocks Claude Code from your passwords and keys, and asks you in plain English before risky commands like mass deletes or force-pushes.

## License

MIT
