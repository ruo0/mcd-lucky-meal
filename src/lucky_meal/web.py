"""麦麦今日运势 · 网页版（零依赖，基于标准库 http.server）。

用法:
  python -m lucky_meal.web              # 启动网页，真实连接 mcd-mcp
  python -m lucky_meal.web --port 8777  # 自定义端口

浏览器访问 http://localhost:<port> 即可看到今日运势卡片。
所有 mcd-mcp 调用均为只读工具，与 CLI / WorkBuddy Skill 共用同一套逻辑。
本服务只连接真实 mcd-mcp，不提供内置演示数据；未连接时返回明确的错误提示。
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from . import lucky_meal, mcp_client

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
DEFAULT_PORT = 8777


def build_payload(salt: str) -> tuple[dict, str]:
    url, token = mcp_client.load_mcp_config()
    if not token:
        return (
            {"error": True, "message": "未找到 mcd-mcp 配置：请在 WorkBuddy 启用 mcd-mcp 连接器后重试。"},
            "未连接",
        )
    try:
        with mcp_client.MCPStreamableClient(url, token) as client:
            result, _ = lucky_meal.fetch_and_roll(client, salt=salt)
        return asdict(result), "真实 mcd-mcp 数据"
    except mcp_client.MCPClientError as e:
        return {"error": True, "message": f"真实数据获取失败：{e}"}, "连接失败"


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") in ("", "/index.html"):
            self._serve_static("index.html")
            return
        if parsed.path == "/api/fortune":
            self._serve_fortune(parse_qs(parsed.query))
            return
        if parsed.path.startswith("/static/"):
            self._serve_static(parsed.path[len("/static/"):])
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def _serve_static(self, name: str) -> None:
        path = (STATIC_DIR / name).resolve()
        if not str(path).startswith(str(STATIC_DIR.resolve())) or not path.exists():
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        ctype = "text/html; charset=utf-8" if name.endswith(".html") else "application/octet-stream"
        self._send(200, path.read_bytes(), ctype)

    def _serve_fortune(self, qs: dict) -> None:
        salt = qs.get("salt", [""])[0]
        data, source = build_payload(salt)
        payload = json.dumps({"source": source, **data}, ensure_ascii=False).encode("utf-8")
        self._send(200, payload, "application/json; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lucky-meal-web", description="麦麦今日运势 · 网页版")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="监听端口")
    args = parser.parse_args(argv)

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"麦麦今日运势已启动 → http://{args.host}:{args.port}  (Ctrl+C 退出)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
