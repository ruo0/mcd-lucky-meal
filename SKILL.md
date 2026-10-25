---
name: lucky-meal
description: 麦麦今日运势 · 基于麦当劳 mcd-mcp 的趣味运势 Skill。当用户提到「今天麦当劳运势 / 幸运餐 / 今日宜忌 / 今天有什么活动 / 我有什么券 / 该不该抽奖」时启用；先并行调用 mcd-mcp 只读工具（now-time-info、list-nutrition-foods、campaign-calendar、query-lottery-info、available-coupons），再用确定性运势引擎生成可复现的今日运势报告。全程只读，绝不自动下单或自动抽奖。
---

# 麦麦今日运势 · Lucky Meal

把麦当劳的真实数据变成一份「今日运势签」：用当前时间做种子，串起门店营养库、当月活动、抽奖资格与可领券，输出一张克制精致的运势卡。

## 触发场景

- 「看看我今天麦当劳运势」「给我算个今日幸运餐」
- 「今天麦当劳有什么活动 / 我有什么券能领 / 现在该不该去抽奖」
- 任何想把「吃麦当劳」和「趣味占卜 / 决策辅助」结合的需求

## 工作流

1. **取时间种子**：调用 `mcp__mcd-mcp__now-time-info`，拿到 `data.timestamp`（毫秒）、`data.date`、`data.dayOfWeek`。
2. **并行拉取真实数据**（只读，互不依赖，可一起调用）：
   - `mcp__mcd-mcp__list-nutrition-foods` → 160 个真实餐品的营养池，作为「幸运餐单」候选。
   - `mcp__mcd-mcp__campaign-calendar` → 当月活动；取 `data.dailyList` 中 `date == 今天` 的那天的 `events[].articleDto.title` 作为「运势加成 buff」。
   - `mcp__mcd-mcp__query-lottery-info` → 抽奖资格；看 `data.drawDecision.resourceEligible` 与 `data.drawDecision.nextConsumption` 决定「今日宜不宜抽奖」。
   - `mcp__mcd-mcp__available-coupons` → `data[]` 中 `couponStatus == "CAN_GET"` 的即为今日可领彩蛋。
3. **生成运势**：用 `src/lucky_meal/fortune_engine.py` 的 `roll_fortune(ts, ...)`，以时间戳为确定性种子，产出幸运数字、五行、运势指数、幸运餐单、宜忌、签文、活动加成、抽奖建议、隐藏彩蛋。
4. **渲染**：用 `src/lucky_meal/ui_text.py` 的 `render_fortune` 输出一张等宽边框运势卡（中文按显示宽度对齐）。

## 在 WorkBuddy 内直接运行

项目已自带零依赖 CLI，连接本机已启用的 mcd-mcp 即可：

```bash
cd src
python -m lucky_meal.cli            # 真实连接 mcd-mcp
```

若只需快速体验，也可直接执行下方独立脚本（读 `~/.workbuddy/mcp.json` 里的 mcd-mcp 配置）：

```python
import sys, json
sys.path.insert(0, "src")
from lucky_meal import lucky_meal, mcp_client

url, token = mcp_client.load_mcp_config()
with mcp_client.MCPStreamableClient(url, token) as client:
    result, _ = lucky_meal.fetch_and_roll(client)
print(lucky_meal.render(result))
```

## 合规边界（务必遵守）

- 仅调用**只读**工具；`create-order` / `draw-lottery` / `mall-create-order` 等写操作**绝不在本 Skill 内自动触发**。
- 若用户主动要求下单或抽奖，先引导其到麦当劳 App 完成，并在调用 `draw-lottery` 前必须向其展示 `query-lottery-info` 的 `drawDecision.nextConsumption` 并获得明确确认。
- 运势结果为娱乐性质，输出时需注明「仅供娱乐，理性消费」。
