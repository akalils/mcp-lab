
# 知识库代码留在旁边的 RAGuard 项目里。
import sys
from pathlib import Path

RAGUARD_ROOT = Path(__file__).resolve().parents[2] / "RAGuard"
if not (RAGUARD_ROOT / "raguard" / "knowledge_service.py").is_file():
    raise SystemExit(f"找不到 RAGuard 知识库代码：{RAGUARD_ROOT}")
sys.path.insert(0, str(RAGUARD_ROOT))

from typing import Any
from mcp.server.fastmcp import FastMCP

from raguard.knowledge_service import QueryText, ResultLimit, search
mcp = FastMCP("RAGuard Learning")

@mcp.tool(
    name="search_knowledge",
    description="搜索本地知识库，返回相关原文片段和来源，不生成回答。",
    structured_output=True,
)

def search_knowledge(query: QueryText, top_k: ResultLimit=3) -> dict[str, Any]:
    return search(query, top_k)

if __name__ == "__main__":
    mcp.run(transport="stdio")