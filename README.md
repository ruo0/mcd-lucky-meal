# 麦麦今日运势 · Lucky Meal

> 基于麦当劳官方 **mcd-mcp** 的趣味运势 Skill —— 用真实门店数据，给你一张「今日运势签」。

## 这是什么

一个把「吃麦当劳」和「趣味占卜 / 决策辅助」结合的创新 Skill。当你问「今天麦当劳运势怎么样」时，它会调用
麦当劳 MCP 的只读接口，拉取真实的时间、营养库、本月活动、抽奖资格与可领券，再用一个**确定性运势引擎**
生成一份可复现的今日运势卡：幸运数字、五行宜忌、今日幸运餐单、活动加成、抽奖建议、隐藏彩蛋。

## 亮点

- **真实数据驱动**：幸运餐单来自麦当劳 160 个真实餐品的营养库，不是瞎编。
- **确定性可复现**：以毫秒时间戳为种子，同一天结果稳定，适合评审与复现。
- **安全合规**：全程只读，绝不下单、绝不自动抽奖；写操作严格遵循 mcd-mcp 的确认约束。
- **三形态交付**：可直接装在 WorkBuddy 的 Skill、零依赖命令行程序，以及零依赖网页版（麦当劳红 + 金拱门黄配色，毛玻璃卡片）。
- **克制设计**：黑白编辑风，网页版融入麦当劳品牌色（红 `#da291c` / 金 `#ffc72c`）作为强调色。

## 安装

### 形态 A：WorkBuddy Skill

将整个仓库放入 WorkBuddy 的 skills 目录（用户级 `~/.workbuddy/skills/` 或项目级 `.workbuddy/skills/`），
并确保已在连接器管理页启用 `mcd-mcp`（配置位于 `~/.workbuddy/mcp.json`）。启用后通过对话即可触发
（见 `SKILL.md` 的触发词）。

### 形态 B：独立 Python 程序

```bash
cd src
python -m lucky_meal.cli            # 连接真实 mcd-mcp（自动读取 ~/.workbuddy/mcp.json）
```

> 仅依赖 Python 3.10+ 标准库，**无需 `pip install`**。真实模式下请确保本机已启用 mcd-mcp。

### 形态 C：网页版（麦当劳配色）

```bash
cd src
python -m lucky_meal.web                 # 启动网页，真实连接 mcd-mcp
python -m lucky_meal.web --port 8777     # 自定义端口
```

启动后浏览器打开 `http://localhost:8777` 即可看到今日运势卡片：
- 黑白编辑风卡片 + 毛玻璃质感，强调色使用麦当劳红 `#da291c` 与金拱门黄 `#ffc72c`
- 卡片内展示：运势指数（带计数动画）、幸运数字 / 五行、幸运餐单、今日宜忌、签文、活动加成、隐藏彩蛋、抽奖建议
- 支持「再抽一次」（换种子重算）重新占卜
- 后端 `/api/fortune` 复用同一套运势引擎与 MCP 客户端，零第三方依赖

## 使用示例

```text
$ python -m lucky_meal.cli
┌────────────────────────────────────────┐
│           麦 麦 今 日 运 势            │
│  2026-10-25   周日                     │
├────────────────────────────────────────┤
│  幸运数字    3                         │
│  今日五行    金 · 钠 / 钙              │
│  运势指数    ████░░░░░░ 44 平          │
│  今日宜忌    宜约饭谈事 / 忌空腹硬扛   │
├────────────────────────────────────────┤
│  今日幸运餐单                          │
│    主食   锡兰红茶                     │
│    小食   麦辣鸡翅                     │
│    饮品   无糖可口可乐                 │
├────────────────────────────────────────┤
│  签文   「甜筒转个圈，快乐不用甜。」   │
│  活动加成   今日运势 +6，因为「...」   │
│  抽奖建议   今日宜抽奖！...            │
│  隐藏彩蛋   今天有 1 张券可领...       │
└────────────────────────────────────────┘
```

真实模式会从 mcd-mcp 拉取你账户当下的活动、券与抽奖资格。

## 目标用户

- 麦当劳重度用户 / 想「薅羊毛」又爱玩梗的年轻人
- 运营 / 市场同学：可作为会员活跃、活动曝光的轻互动玩法原型
- 开发者：展示如何基于 mcd-mcp 组合多个只读工具做创意应用

## 项目结构

```text
lucky-meal/
├── README.md                 # 本文件
├── CONTEST_DECLARATION.md    # 参赛声明
├── MCP_INTEGRATION.md        # mcd-mcp 接入说明
├── SKILL.md                  # WorkBuddy Skill 定义
├── pyproject.toml / requirements.txt
├── src/lucky_meal/
│   ├── fortune_engine.py     # 确定性运势引擎（纯函数，可单测）
│   ├── mcp_client.py        # 零依赖 MCP Streamable HTTP 客户端
│   ├── lucky_meal.py        # 编排：拉取 → 解析 → 运势
│   ├── ui_text.py           # 运势卡渲染（中文显示宽度对齐）
│   ├── cli.py               # 命令行入口
│   └── web.py               # 网页版（标准库 http.server + /api/fortune）
├── static/index.html         # 麦当劳配色运势卡片页（零依赖前端）
├── tests/test_fortune_engine.py
└── workbuddy.md             # WorkBuddy 开发上下文导出
```

## 合规说明

本项目仅使用 mcd-mcp 的**只读**工具，不涉及 `create-order` / `draw-lottery` / `mall-create-order` 等写操作，
完全符合 mcd-mcp 调用规范与赛事合规要求。详见 `MCP_INTEGRATION.md` 与 `CONTEST_DECLARATION.md`。
