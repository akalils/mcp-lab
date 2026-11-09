# mcp-lab

MCP 练习项目，和旁边的 [RAGuard](../RAGuard) 分开。这里只有 MCP 服务、教学 demo 和探针。法律检索、向量库和评测仍在 RAGuard。

`servers/mcp_server.py` 会把旁边的 `../RAGuard` 加入导入路径，再调用那边的 `raguard.knowledge_service`。其余 demo 只使用进程内存，不读取 RAGuard。

启动方式和练习入口见 [docs/MCP_LAB.md](docs/MCP_LAB.md)。

```bash
pip install -r requirements.txt
```

`search_knowledge` 还需要 RAGuard 里已经装好的检索依赖、`.env` 和 `data/chroma_db`。
