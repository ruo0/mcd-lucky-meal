# MCP 接入说明（MCP_INTEGRATION.md）

本文档说明本项目实际使用的麦当劳 MCP Server、Tool、调用流程与业务价值。所有调用均为**只读**，不涉及下单与抽奖。

## 1. 实际使用的 MCP Server

| 项 | 值 |
|---|---|
| Server 名称 | `mcd-mcp` |
| 接入方式 | Streamable HTTP（`streamablehttp`） |
| 服务地址 | `https://mcp.mcd.cn` |
| 鉴权 | `Authorization: Bearer <token>`（token 存放于本机 `~/.workbuddy/mcp.json`，不入库） |
| 协议版本 | `2024-11-05` |
| 客户端实现 | `src/lucky_meal/mcp_client.py`，仅用 Python 标准库 `urllib` 实现，零第三方依赖 |

> 关键实现细节：mcd-mcp 的 `tools/call` 响应优先返回 **`structuredContent`**（干净 JSON），
> `content[].text` 仅为人读说明。因此 `mcp_client.call_tool` 优先解析 `structuredContent`，
> 避免了对 Markdown 说明文本做脆弱的正则解析。

## 2. 实际使用的 Tool（5 个只读工具）

| 工具 | 用途 | 关键返回字段 | 在本项目中的作用 |
|---|---|---|---|
| `now-time-info` | 取当前时间 | `data.timestamp`(毫秒)、`data.date`、`data.dayOfWeek`、`data.formatted` | **运势种子**：以毫秒时间戳驱动确定性伪随机，保证同一天结果稳定 |
| `list-nutrition-foods` | 餐品营养库 | `data` 为 `[160]{productName,energyKcal,...}` 文本表 | **幸运餐单候选池**：从中抽取今日主食/小食/饮品 |
| `campaign-calendar` | 当月活动日历 | `data.dailyList[].date`、`events[].articleDto.title` | **活动加成 buff**：取今日活动的标题，提升运势值并展示 |
| `query-lottery-info` | 积分抽奖资格 | `data.drawDecision.resourceEligible`、`data.drawDecision.nextConsumption` | **抽奖建议**：判断是否「今日宜抽奖」及本次消耗 |
| `available-coupons` | 可领优惠券 | `data[].couponName`、`data[].couponStatus`(`CAN_GET`=可领取) | **隐藏彩蛋**：提示今日可领的券 |

## 3. 调用流程（时序）

```text
用户提问
   │
   ▼
[now-time-info] ──────────────┐ 取时间戳 + 日期 + 星期
                               │
[list-nutrition-foods] ────────┤ 解析出 160 个真实餐品 → 营养池
                               │
[campaign-calendar] ───────────┤ 取 dailyList 中 date==今日 的 events 标题
                               │
[query-lottery-info] ──────────┤ 取 drawDecision（资源是否充足 + 本次消耗）
                               │
[available-coupons] ───────────┘ 取 couponStatus==CAN_GET 的券
                               │
                               ▼
                  运势引擎 roll_fortune(ts, ...)
                  （确定性种子：时间戳 + 可选用户盐值）
                               │
                               ▼
                  ui_text.render_fortune() → 运势卡
```

五个工具彼此独立（仅 `now-time-info` 的日期用于过滤 `campaign-calendar`），可并行调用以降延迟。

## 4. 关键返回结构示例（已用真实返回校验）

`campaign-calendar`：
```json
{ "data": { "dailyList": [
  { "date": "2026-10-25", "dateText": "2026年10月25日 今日",
    "events": [ { "articleDto": { "title": "麦当劳「我就喜欢」限定丝巾正式开售🔥" } } ] }
] } }
```

`available-coupons`：
```json
{ "data": [
  { "couponName": "免费脆薯饼", "couponStatus": "CAN_GET", "label": "可领取" },
  { "couponName": "11.9元麦辣鸡腿堡", "couponStatus": "HAVING_RECEIVE", "label": "已领取" }
] }
```

`query-lottery-info`：
```json
{ "data": { "drawDecision": { "resourceEligible": true,
  "nextConsumption": { "type": "POINTS", "points": "24" } },
  "availablePoint": "39.7" } }
```

## 5. 业务价值

- **把「数据」变成「体验」**：将麦当劳分散的门店/活动/权益数据，通过轻量创意编排成一则可分享的「运势」，提升会员互动与活动曝光。
- **可运营的钩子**：活动加成、可领券彩蛋、抽奖建议都是天然的流量入口，可引导用户进入对应活动页。
- **安全可落地**：全程只读、确定性可复现，既满足评审要求，也规避了自动下单/抽奖的合规风险。
- **可扩展**：运势引擎与 MCP 客户端解耦，后续接入 `query-nearby-stores` / `query-meals` 即可升级为「按门店生成幸运餐单 + 一键下单」的完整链路。
