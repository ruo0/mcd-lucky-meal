"""麦麦今日运势 · 命令行入口。

用法：
  python -m lucky_meal.cli                 # 连接真实 mcd-mcp（需 ~/.workbuddy/mcp.json 已配置）
  python -m lucky_meal.cli --user 小明      # 用昵称做运势盐值，不同人不同签
"""

from __future__ import annotations

import argparse
import sys

from . import lucky_meal, mcp_client


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lucky-meal", description="麦麦今日运势 · Lucky Meal")
    parser.add_argument("--user", default="", help="用户昵称，作为运势盐值")
    parser.add_argument("--url", default=None, help="覆盖 mcd-mcp 地址")
    parser.add_argument("--token", default=None, help="覆盖 mcd-mcp Bearer token")
    args = parser.parse_args(argv)

    salt = args.user or ""

    url, token = mcp_client.load_mcp_config()
    url = args.url or url
    token = args.token or token
    if not token:
        print("未找到 mcd-mcp token：请先在 WorkBuddy 启用 mcd-mcp，或用 --token 指定。", file=sys.stderr)
        return 2

    try:
        with mcp_client.MCPStreamableClient(url, token) as client:
            result, _ = lucky_meal.fetch_and_roll(client, salt=salt)
        print(lucky_meal.render(result))
        return 0
    except mcp_client.MCPClientError as e:
        print(f"调用 mcd-mcp 失败：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
