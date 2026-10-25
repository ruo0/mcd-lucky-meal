"""基于标准库 urllib 的 MCP Streamable HTTP 客户端（零第三方依赖）。

仅实现本项目所需最小子集：initialize / notifications.initialized / tools.list / tools.call。
适配 mcd-mcp（https://mcp.mcd.cn，Bearer 鉴权）。
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_URL = "https://mcp.mcd.cn"
CONFIG_PATH = Path.home() / ".workbuddy" / "mcp.json"


class MCPClientError(RuntimeError):
    pass


class MCPStreamableClient:
    def __init__(self, url: str, token: str, timeout: int = 30):
        self.url = url
        self.token = token
        self.timeout = timeout
        self.session_id = None
        self._id = 0
        self._initialized = False

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.token}",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return headers

    def _post(self, payload: dict) -> Any:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.url, data=data, headers=self._headers(), method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                ctype = resp.headers.get("Content-Type", "")
                sid = resp.headers.get("Mcp-Session-Id")
                if sid:
                    self.session_id = sid
        except urllib.error.HTTPError as e:
            raise MCPClientError(
                f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}"
            ) from e
        return self._decode(raw, ctype)

    @staticmethod
    def _decode(raw: str, ctype: str) -> Any:
        if "text/event-stream" in ctype:
            last = None
            for line in raw.splitlines():
                line = line.strip()
                if line.startswith("data:"):
                    chunk = line[len("data:"):].strip()
                    if chunk:
                        try:
                            last = json.loads(chunk)
                        except json.JSONDecodeError:
                            continue
            return last
        if not raw.strip():
            return None
        return json.loads(raw)

    def initialize(self) -> Any:
        resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "lucky-meal", "version": "1.0.0"},
            },
        })
        if not resp or "result" not in resp:
            raise MCPClientError(f"initialize 失败: {resp}")
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        self._initialized = True
        return resp["result"]

    def list_tools(self) -> list[dict]:
        resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {},
        })
        return (resp or {}).get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict | None = None) -> str:
        if not self._initialized:
            self.initialize()
        resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        })
        result = (resp or {}).get("result")
        if result is None:
            raise MCPClientError(f"{name} 返回异常: {resp}")
        if result.get("isError"):
            raise MCPClientError(f"{name} 执行失败: {result}")
        structured = result.get("structuredContent")
        if isinstance(structured, (dict, list)):
            return json.dumps(structured, ensure_ascii=False)
        texts = [
            c.get("text", "")
            for c in result.get("content", [])
            if c.get("type") == "text"
        ]
        return "\n".join(texts)

    def close(self) -> None:
        self._initialized = False

    def __enter__(self) -> "MCPStreamableClient":
        self.initialize()
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def load_mcp_config() -> tuple[str, str]:
    if CONFIG_PATH.exists():
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        srv = cfg.get("mcpServers", {}).get("mcd-mcp", {})
        url = srv.get("url", DEFAULT_URL)
        auth = srv.get("headers", {}).get("Authorization", "")
        token = auth.replace("Bearer ", "", 1).strip()
        return url, token
    return DEFAULT_URL, os.environ.get("MCD_MCP_TOKEN", "")
