"""Budget Coach Lite: a Claude Code status line that forecasts when you'll hit your usage limit.

Claude Code pipes session JSON to this script on stdin; it prints one status line.
It remembers recent 5-hour usage readings to measure your burn rate, then predicts
whether you'll run out before the window resets.

Shows: model | 5h usage bar + reset time | forecast | weekly % | context %
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

STATE_DIR = Path(os.environ.get("BUDGET_COACH_DIR", Path.home() / ".claude" / "budget-coach"))
SAMPLES = STATE_DIR / "samples.json"
RATE_WINDOW = 30 * 60  # measure burn rate over the last 30 minutes
MIN_SPAN = 3 * 60      # need at least 3 minutes of readings before forecasting

GREEN, YELLOW, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"


def color(pct):
    return GREEN if pct < 50 else YELLOW if pct < 80 else RED


def bar(pct, width=10):
    """Solid colored blocks for used, dim dots for remaining, readable in any terminal font."""
    filled = round(min(max(pct, 0), 100) / 100 * width)
    return f"{color(pct)}{'█' * filled}{RESET}{DIM}{'·' * (width - filled)}{RESET}"


def clock(ts):
    t = datetime.fromtimestamp(ts)
    return f"{t.hour % 12 or 12}:{t.minute:02d}{'am' if t.hour < 12 else 'pm'}"


def load_samples():
    try:
        return json.loads(SAMPLES.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def record(now, pct, resets_at):
    """Store this reading; keep only the current window's last 30 minutes."""
    samples = [s for s in load_samples()
               if s[2] == resets_at and now - s[0] <= RATE_WINDOW and s[1] <= pct]
    if not samples or now - samples[-1][0] >= 20:  # at most one reading per 20s
        samples.append([now, pct, resets_at])
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        SAMPLES.write_text(json.dumps(samples), encoding="utf-8")
    except OSError:
        pass  # a read-only home dir shouldn't break the status line
    return samples


def forecast(now, pct, resets_at, samples):
    """Return (hit_time or None, enough_data)."""
    first = samples[0]
    span = now - first[0]
    if span < MIN_SPAN:
        return None, False
    rate = (pct - first[1]) / span  # percent per second
    if rate <= 0:
        return None, True
    hit = now + (100 - pct) / rate
    return (hit if hit < resets_at else None), True


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    now = time.time()
    parts = [data.get("model", {}).get("display_name") or "Claude"]
    model_id = (data.get("model", {}).get("id") or "").lower()

    five = (data.get("rate_limits") or {}).get("five_hour") or {}
    pct, resets_at = five.get("used_percentage"), five.get("resets_at")
    if pct is None or not resets_at:
        parts.append(f"{DIM}5h usage shows after the first reply{RESET}")
    else:
        parts.append(f"5h {bar(pct)} {color(pct)}{pct:.0f}%{RESET} {DIM}resets {clock(resets_at)}{RESET}")
        hit, enough = forecast(now, pct, resets_at, record(now, pct, resets_at))
        if hit:
            tip = "try /model sonnet" if "opus" in model_id else "try /compact or a fresh session"
            parts.append(f"{RED}⚠ limit ~{clock(hit)} at this pace · {tip}{RESET}")
        elif enough:
            parts.append(f"{GREEN}✓ on pace to last until reset{RESET}")
        else:
            parts.append(f"{DIM}measuring pace…{RESET}")

    week = ((data.get("rate_limits") or {}).get("seven_day") or {}).get("used_percentage")
    if week is not None:
        parts.append(f"wk {color(week)}{week:.0f}%{RESET}")

    ctx = (data.get("context_window") or {}).get("used_percentage")
    if ctx is not None:
        hint = f" {DIM}(/compact saves usage){RESET}" if ctx >= 60 else ""
        parts.append(f"ctx {color(ctx)}{ctx:.0f}%{RESET}{hint}")

    print(f" {DIM}│{RESET} ".join(parts))


if __name__ == "__main__":
    main()
