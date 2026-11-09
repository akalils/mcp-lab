"""本地 Bearer 生命周期教学；固定假凭证，不实现浏览器 OAuth。"""

import json
import os
import sys
import time
from pathlib import Path

import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

STATE_FILE = Path(__file__).with_suffix(".auth-state.json")
mcp = FastMCP("MCP Auth Demo", stateless_http=True, json_response=True)


def read_state():
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state):
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state), encoding="utf-8")
    temporary.chmod(0o600)
    os.replace(temporary, STATE_FILE)


def issue(previous=None):
    generation = (previous or {}).get("generation", 0) + 1
    state = {
        "generation": generation,
        "access_token": f"lab-access-{generation}",
        "refresh_token": f"lab-refresh-{generation}",
        "expires_at": int(time.time()) + 600,
        "revoked": False,
    }
    save_state(state)
    return state


@mcp.tool()
def auth_ping() -> dict[str, str]:
    """只有通过 HTTP 凭证检查后，才会执行这个只读工具。"""
    return {"message": "认证通过，工具调用成功"}


class BearerGate:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].rstrip("/") == "/mcp":
            header = dict(scope["headers"]).get(b"authorization", b"").decode("latin-1")
            state = read_state()
            if not header:
                error = "MISSING_BEARER"
            elif header != "Bearer " + state["access_token"]:
                error = "INVALID_TOKEN"
            elif state["revoked"]:
                error = "TOKEN_REVOKED"
            elif time.time() >= state["expires_at"]:
                error = "TOKEN_EXPIRED"
            else:
                error = None
            if error:
                response = JSONResponse(
                    {"error": error},
                    status_code=401,
                    headers={"WWW-Authenticate": 'Bearer realm="mcp-auth-lab"'},
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "help"
    if action == "issue":
        previous = read_state() if STATE_FILE.exists() else None
        result = issue(previous)
    elif action == "serve":
        if not STATE_FILE.exists():
            raise SystemExit("请先运行 issue，生成本地假凭证")
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8877
        uvicorn.run(BearerGate(mcp.streamable_http_app()), host="127.0.0.1", port=port)
        return
    elif action in {"expire", "refresh", "revoke"}:
        state = read_state()
        if action == "expire":
            state["expires_at"] = int(time.time()) - 1
            save_state(state)
            result = {"status": "expired"}
        elif action == "revoke":
            state["revoked"] = True
            save_state(state)
            result = {"status": "revoked"}
        else:
            supplied = sys.argv[2] if len(sys.argv) > 2 else ""
            if state["revoked"] or supplied != state["refresh_token"]:
                raise SystemExit("REFRESH_DENIED")
            result = issue(state)
    else:
        raise SystemExit("用法：issue | serve [端口] | expire | refresh 假刷新凭证 | revoke")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()