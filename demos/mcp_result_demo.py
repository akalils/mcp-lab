"""独立 MCP 返回结果教学服务，无模型、数据库或文件写入。"""

from typing import Literal
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("MCP Result Demo")
class DemoHit(BaseModel):
    content: str
    source: str

class DemoResult(BaseModel):
    results: list[DemoHit]

@mcp.tool(structured_output=True)
def demo_lookup(mode: Literal["found", "empty", "error"]) -> DemoResult:
    """教学模式：found 返回一条，empty 返回空数组，error 模拟执行失败。"""
    if mode == "error":
        raise RuntimeError("DEMO_BACKEND_UNAVALIABLE")
    rows = []
    if mode == "found":
        rows.append(DemoHit(content="这是一条演示结果", source="demo"))
    return DemoResult(results=rows)

if __name__ == "__main__":
    mcp.run(transport="stdio")