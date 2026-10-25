"""运势报告文本渲染（克制黑白编辑风，按显示宽度对齐 + 长字段折行）。"""

from __future__ import annotations

import unicodedata

from .fortune_engine import FortuneResult

W = 40

WEEKDAYS = {
    "MONDAY": "周一", "TUESDAY": "周二", "WEDNESDAY": "周三",
    "THURSDAY": "周四", "FRIDAY": "周五", "SATURDAY": "周六", "SUNDAY": "周日",
}


def _dwidth(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def _pad(s: str, width: int) -> str:
    return s + " " * max(0, width - _dwidth(s))


def _center(s: str, width: int) -> str:
    total = width - _dwidth(s)
    left = max(0, total // 2)
    right = max(0, total - left)
    return " " * left + s + " " * right


def _top() -> str:
    return "┌" + "─" * W + "┐"


def _bot() -> str:
    return "└" + "─" * W + "┘"


def _sep() -> str:
    return "├" + "─" * W + "┤"


def _title(s: str) -> str:
    return "│" + _center(s, W) + "│"


def _line(s: str) -> str:
    return "│" + _pad(s, W) + "│"


def _wrap(text: str, width: int) -> list[str]:
    lines: list[str] = []
    cur = ""
    cw = 0
    for ch in text:
        w = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if cw + w > width:
            lines.append(cur)
            cur = ch
            cw = w
        else:
            cur += ch
            cw += w
    if cur:
        lines.append(cur)
    return lines or [""]


def _kv(prefix: str, text: str) -> list[str]:
    pre_w = _dwidth(prefix)
    avail = W - pre_w
    wrapped = _wrap(text, avail)
    out: list[str] = []
    for i, ln in enumerate(wrapped):
        out.append(_line(prefix + ln if i == 0 else " " * pre_w + ln))
    return out


def render_fortune(f: FortuneResult) -> str:
    bar_len = 10
    filled = round(f.fortune_score / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    weekday = WEEKDAYS.get(f.day_of_week, f.day_of_week)

    lines = [
        _top(),
        _title("麦 麦 今 日 运 势"),
        _line(f"  {f.date}   {weekday}"),
        _sep(),
        _line(f"  幸运数字    {f.lucky_number}"),
        _line(f"  今日五行    {f.element} · {f.element_nutrient}"),
        _line(f"  运势指数    {bar} {f.fortune_score} {f.fortune_level}"),
        _line(f"  今日宜忌    {f.yi} / {f.ji}"),
        _sep(),
        _line("  今日幸运餐单"),
        _line(f"    主食   {f.lucky_main}"),
        _line(f"    小食   {f.lucky_side}"),
        _line(f"    饮品   {f.lucky_drink}"),
        _sep(),
        _line(f"  签文   「{f.poem}」"),
    ]
    if f.campaign_buff:
        lines += _kv("  活动加成   ", f.campaign_buff)
    lines += _kv("  抽奖建议   ", f.lottery_advice)
    lines += _kv("  隐藏彩蛋   ", f.coupon_egg)
    lines.append(_bot())
    return "\n".join(lines)
