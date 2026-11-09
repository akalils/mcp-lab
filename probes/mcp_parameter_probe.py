"""用 MCP stdio 客户端观察参数处理；使用运行服务的同一 Python 环境。"""

import asyncio
import json
import sys
from datetime import timedelta
from importlib.metadata import version
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import McpError


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


async def main(server_path):
    server_path = Path(server_path).expanduser().resolve(strict=True)
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        cwd=str(server_path.parent),
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(
            read, write, read_timeout_seconds=timedelta(seconds=60)
        ) as session:
            initialized = await session.initialize()
            cursor = None
            while True:
                listing = await session.list_tools(cursor=cursor)
                tool = next(
                    (t for t in listing.tools if t.name == "search_knowledge"), None
                )
                if tool is not None:
                    break
                cursor = listing.nextCursor
                if not cursor:
                    raise RuntimeError("工具目录中没有 search_knowledge")
            emit({
                "kind": "definition", "client_mcp_version": version("mcp"),
                "server": initialized.serverInfo.model_dump(),
                "protocolVersion": initialized.protocolVersion,
                "inputSchema": tool.inputSchema,
            })
            cases = [
                ("missing_query", {"top_k": 3}),
                ("string_top_k", {"query": "MCP 参数练习", "top_k": "3"}),
                ("extra_argument", {
                    "query": "MCP 参数练习", "top_k": 1, "extra_probe": True
                }),
            ]
            for name, arguments in cases:
                report = {"case": name, "arguments": arguments}
                try:
                    result = await session.call_tool("search_knowledge", arguments)
                    report["isError"] = result.isError
                    if result.isError:
                        report["messages"] = [
                            c.text[:1000] for c in result.content if c.type == "text"
                        ]
                    else:
                        data = result.structuredContent
                        if isinstance(data, dict) and isinstance(data.get("results"), list):
                            report["result_count"] = len(data["results"])
                except McpError as exc:
                    report["protocol_error"] = exc.error.model_dump(exclude_none=True)
                emit(report)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("用法：python probes/mcp_parameter_probe.py /绝对路径/servers/mcp_server.py")
    asyncio.run(main(sys.argv[1]))