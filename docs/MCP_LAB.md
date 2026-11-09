# MCP 练习入口

## 三类文件

- **servers**：`mcp_server.py` 注册 `search_knowledge`，调用旁边 RAGuard 项目的 `raguard/knowledge_service.py` 检索已有向量库。
- **demos**：`mcp_side_effect_demo.py` 提供商品、预览、慢调用、指令干扰和 echo 工具，仅使用进程内存。`mcp_permission_demo.py`、`mcp_result_demo.py`、`mcp_auth_demo.py` 也是独立演示。
- **probes**：两个客户端脚本通过真实 MCP stdio 连接服务，分别观察参数校验和并发返回。

不要把 Python 包目录命名为 `mcp/`，以免覆盖已安装的 `mcp` SDK。本项目目录使用 `mcp-lab`。

## Inspector 连接

Command 继续使用已有环境：

```text
/opt/anaconda3/envs/lisheng/bin/python
```

Arguments 按练习对象选择以下一个绝对路径：

```text
/Users/cwill/Project/mcp-lab/servers/mcp_server.py
/Users/cwill/Project/mcp-lab/demos/mcp_side_effect_demo.py
/Users/cwill/Project/mcp-lab/demos/mcp_permission_demo.py
/Users/cwill/Project/mcp-lab/demos/mcp_result_demo.py
```

每个连接只填写一个服务脚本。旧连接需要断开后更新 Arguments，再重新连接。Codex 中已经启动的服务也需重新加载连接或重启客户端，新配置才会生效。

认证演示使用 HTTP，不走上面的 stdio Inspector 参数：

```bash
/opt/anaconda3/envs/lisheng/bin/python /Users/cwill/Project/mcp-lab/demos/mcp_auth_demo.py issue
/opt/anaconda3/envs/lisheng/bin/python /Users/cwill/Project/mcp-lab/demos/mcp_auth_demo.py serve
```

## 参数与并发练习

在本项目根目录执行：

```bash
/opt/anaconda3/envs/lisheng/bin/python probes/mcp_parameter_probe.py /Users/cwill/Project/mcp-lab/servers/mcp_server.py

/opt/anaconda3/envs/lisheng/bin/python probes/mcp_load_probe.py /Users/cwill/Project/mcp-lab/demos/mcp_side_effect_demo.py
```

也可以给调用脚本和服务脚本都使用绝对路径，从任意目录启动。参数探针的合法查询会实际加载本地模型并检索 RAGuard 的向量库；并发探针只调用 demo 的 `echo_probe`。

## 权限 demo

用这个路径配置 Inspector：

```text
/Users/cwill/Project/mcp-lab/demos/mcp_permission_demo.py
```

它是独立服务，不需要粘进商品 demo 中。第一轮使用 `DEMO_ROLE=reader`、`DEMO_SHOP=shop-a`；下一轮将角色改为 `editor`，保持店铺不变，再启动新服务进程。先调用 `get_access_context` 确认实际角色和店铺。
