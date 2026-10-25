"""编排层：拉取 mcd-mcp 数据 → 解析 → 运势引擎 → 报告。

所有调用均为只读工具（时间/营养/活动/抽奖资格/可领券），不涉及下单与抽奖，
符合 mcd-mcp 的合规约束。本模块只连接真实 mcd-mcp，不内置演示数据。
"""

from __future__ import annotations

import json
import re

from . import fortune_engine, mcp_client
from .fortune_engine import FortuneResult
from .ui_text import render_fortune


def parse_nutrition(data_str: str) -> list[dict]:
    m = re.search(r"\{([^}]*)\}", data_str)
    fields = [f.strip() for f in m.group(1).split(",")] if m else []
    body = data_str.split(":", 1)[1] if ":" in data_str else data_str
    pool = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < len(fields):
            continue
        row = dict(zip(fields, parts))
        if row.get("productName"):
            pool.append({"productName": row["productName"]})
    return pool


def parse_campaign_today(raw: str, today_str: str) -> list[str]:
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    daily = (obj.get("data") or {}).get("dailyList") or []
    titles: list[str] = []
    for day in daily:
        if day.get("date") != today_str:
            continue
        for ev in day.get("events") or []:
            title = (ev.get("articleDto") or {}).get("title") or ev.get("activityTitle")
            if title:
                titles.append(re.sub(r"[`*#]", "", title).strip())
    return titles


def parse_coupons(raw: str) -> list[dict]:
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    data = obj.get("data") or []
    if not isinstance(data, list):
        return []
    coupons: list[dict] = []
    for c in data:
        coupons.append({
            "title": c.get("couponName", ""),
            "status": c.get("label") or c.get("couponStatus") or "",
        })
    return coupons


def fetch_and_roll(client: mcp_client.MCPStreamableClient, *, salt: str = "") -> tuple[FortuneResult, dict]:
    now = json.loads(client.call_tool("now-time-info"))["data"]
    nut_data = json.loads(client.call_tool("list-nutrition-foods"))["data"]
    camp_raw = client.call_tool("campaign-calendar")
    lot_raw = json.loads(client.call_tool("query-lottery-info")).get("data")
    coup_raw = client.call_tool("available-coupons")

    nutrition_pool = parse_nutrition(nut_data)
    today_str = now["date"]
    campaigns_today = parse_campaign_today(camp_raw, today_str)
    coupons = parse_coupons(coup_raw)

    result = fortune_engine.roll_fortune(
        int(now["timestamp"]),
        date=now["date"],
        day_of_week=now.get("dayOfWeek", ""),
        nutrition_pool=nutrition_pool,
        campaigns_today=campaigns_today,
        lottery=lot_raw,
        coupons=coupons,
        salt=salt,
    )
    meta = {
        "now": now,
        "nutrition_count": len(nutrition_pool),
        "campaigns": campaigns_today,
        "lottery": lot_raw,
        "coupons": coupons,
    }
    return result, meta


def render(result: FortuneResult) -> str:
    return render_fortune(result)
