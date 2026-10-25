# WorkBuddy 开发上下文导出（workbuddy.md）

本文件用于核验本项目是否符合 WorkBuddy × 麦当劳 MCP 联动活动奖励条件：项目全程在 **WorkBuddy** 中通过对话驱动完成，
并真实调用了已在本机启用的 **mcd-mcp** 连接器。

## 开发环境

- 客户端：WorkBuddy（Agent 模式），本机已启用 `mcd-mcp`（35 个工具全部加载）。
- 配置位置：`~/.workbuddy/mcp.json`（`mcd-mcp` → `https://mcp.mcd.cn`，Bearer 鉴权）。
- 运行环境：Python 3.13（managed runtime），零第三方依赖。

## 开发过程（对话上下文摘要）

1. **需求确认**：用户要求基于 mcd-mcp 开发创意 Skill，按赛事清单产出 `README.md` / `CONTEST_DECLARATION.md` /
   `MCP_INTEGRATION.md` / 源代码 / `workbuddy.md`。
2. **能力探查**：通过 WorkBuddy 的 ToolSearch + DeferExecuteTool 实际调用 mcd-mcp，逐一验证了
   `now-time-info`、`list-nutrition-foods`、`campaign-calendar`、`query-lottery-info`、`available-coupons`
   的真实返回结构（确认 `tools/call` 优先返回 `structuredContent` 干净 JSON，而非 `content[].text` 的说明文案）。
3. **方向选型**：在「省钱点餐 / 营养配餐 / 派对策划 / 权益管家」之外，用户选择了更具记忆点的「麦麦今日运势」方向。
4. **实现**：产出 WorkBuddy Skill（`SKILL.md`）+ 零依赖独立 Python 程序（`src/lucky_meal/`），
   含确定性运势引擎、MCP Streamable HTTP 客户端、ASCII 运势卡渲染、CLI 与单元测试。
5. **真实验证**：`python -m lucky_meal.cli`（真实模式）成功连接 mcd-mcp 并生成运势卡，
   幸运餐单来自真实 160 个餐品营养库，活动加成 / 可领券彩蛋 / 抽奖建议均取自真实账户数据；
   `tests/test_fortune_engine.py` 全部通过（验证同一时间戳结果可复现）。
6. **合规约束**：全程仅使用只读工具，未触发任何下单 / 抽奖写操作；`SKILL.md` 明确写入写操作的确认约束。

## 关键决策记录

- **真实数据优先**：运势餐单从 `list-nutrition-foods` 真实菜单抽取，而非硬编码，体现「结合真实 MCP 数据」。
- **确定性可复现**：以毫秒时间戳为种子，避免随机性导致演示不可重现。
- **零依赖**：MCP 客户端用标准库 `urllib` 实现，降低评审与部署门槛。
- **CONTEST_DECLARATION.md**：本仓库提供占位模板并醒目标注「须替换为官方原版」，以避免直接使用非官方内容导致违规。

## 交付物清单

```
README.md                 ✅ 项目介绍 / 安装 / 示例 / 目标用户
CONTEST_DECLARATION.md    
MCP_INTEGRATION.md        ✅ 实际使用的 mcd-mcp Server/Tool/流程/价值
src/lucky_meal/*          ✅ 可运行源代码（Skill + 独立程序）
tests/test_fortune_engine.py ✅ 单元测试
examples/sample_output.txt   ✅ 演示输出
workbuddy.md              ✅ 本文件（开发上下文导出）
```
