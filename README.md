<p align="center">
  <img src="https://img.shields.io/badge/麦麦运势-今日宜开心-FFC72C" alt="lucky"/>
  <img src="https://img.shields.io/badge/数据来源-麦当劳官方MCP-DA291C" alt="mcp"/>
  <img src="https://img.shields.io/badge/依赖-零-9c9c9c" alt="zero"/>
</p>

<h1 align="center">🍟 麦麦今日运势 · Lucky Meal 🥤</h1>

<p align="center"><i>「今天该吃哪一款麦当劳？让金拱门替你算一卦～」</i></p>

---

> 一个基于麦当劳官方 **mcd-mcp** 的小占卜 ✨ 它不会替你下单，只会用真实的门店数据，给你写一张软乎乎的「今日运势签」。

## 🌟 这是什么呀

把「吃麦当劳」和「趣味占卜 / 决策辅助」揉在一起的小创意。当你问「今天麦当劳运势怎么样呀」，
它就会乖乖去调用麦当劳 MCP 的只读接口，拉来**真实的时间、营养库、本月活动、抽奖资格和可领券**，
再交给一个**确定性运势引擎**，生成一张今天专属、还能复现的运势卡：

- 🔢 幸运数字
- 🌈 今日五行与宜忌
- 🍔 今日幸运餐单（从 160 款真实餐品里挑）
- 🎁 活动加成 & 抽奖小建议
- 🥚 还藏了一颗小彩蛋

同一天抽，结果稳稳的，不会上午大吉下午翻车～

## 💡 一点点小心思

- **真实数据驱动**：幸运餐单来自麦当劳真实营养库，不是随手编的哦。
- **确定性可复现**：用毫秒时间戳当种子，同一天结果稳定，评审老师随便复现。
- **安全又乖**：全程只读，绝不下单、绝不偷偷抽奖；写操作严格遵循 mcd-mcp 的确认约束。
- **三种形态都给你**：能装进 WorkBuddy 的 Skill、零依赖命令行、还有零依赖网页版（麦当劳红 + 金拱门黄，毛玻璃卡片）。
- **长这样**：黑白编辑风打底，麦当劳红 `#da291c` / 金 `#ffc72c` 当强调色，克制又精致。

## 🛠️ 怎么装（三步就够啦）

### 形态 A：WorkBuddy Skill（最省心）

把整个仓库丢进 WorkBuddy 的 skills 目录（用户级 `~/.workbuddy/skills/` 或项目级 `.workbuddy/skills/`），
然后去连接器管理页把 `mcd-mcp` 启用一下（配置在 `~/.workbuddy/mcp.json`）。
启用后聊两句就能触发啦，触发词见 `SKILL.md`。

### 形态 B：独立 Python 程序（零依赖）

```bash
cd src
python -m lucky_meal.cli            # 连接真实 mcd-mcp（自动读 ~/.workbuddy/mcp.json）
```

> 只依赖 Python 3.10+ 标准库，**不用 `pip install`** 任何东西～ 真实模式记得本机先启用 mcd-mcp 哦。

### 形态 C：网页版（麦当劳配色，最好看）

```bash
cd src
python -m lucky_meal.web                 # 启动网页，真实连接 mcd-mcp
python -m lucky_meal.web --port 8777     # 想换端口就加这个
```

浏览器打开 `http://localhost:8777` 就能看到今日运势卡片：

- 黑白编辑风 + 毛玻璃质感，强调色是麦当劳红 `#da291c` 与金拱门黄 `#ffc72c`
- 卡片里有：运势指数（带计数动画）、幸运数字 / 五行、幸运餐单、今日宜忌、签文、活动加成、隐藏彩蛋、抽奖建议
- 想再算一次就点「再抽一次」，换个种子重新占卜
- 后端 `/api/fortune` 复用同一套运势引擎和 MCP 客户端，依旧零依赖

## 📋 使用示例

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

真实模式下，活动、券和抽奖资格都是你账户当下真实的数据哦。

## 🎯 谁会喜欢它

- 🍟 麦当劳重度用户 / 想薅羊毛又爱玩梗的年轻人
- 📣 运营 / 市场同学：可以当会员活跃、活动曝光的轻互动玩法原型
- 🧑‍💻 开发者：看一眼就懂怎么把 mcd-mcp 的多个只读工具组合起来做创意应用

## 📂 项目小地图

```text
lucky-meal/
├── README.md                 # 本文件（你正在看的可爱版～）
├── CONTEST_DECLARATION.md    # 参赛声明（⚠️ 需替换为官方原版）
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

## 🤝 合规小提示

本项目只用 mcd-mcp 的**只读**工具，绝不碰 `create-order` / `draw-lottery` / `mall-create-order` 这些写操作，
完全符合 mcd-mcp 调用规范和赛事要求。详见 `MCP_INTEGRATION.md` 与 `CONTEST_DECLARATION.md`。

---

<p align="center"><i>愿今天的你，大吉大利，麦麦开心 🍀</i></p>
