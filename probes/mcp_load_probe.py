import asyncio
import json
import statistics
import sys
import time
from datetime import timedelta
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def show(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


async def main():
    server = Path(sys.argv[1]).expanduser().resolve(strict=True)
    params = StdioServerParameters(command=sys.executable, args=[str(server)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            order = []

            async def probe(marker, delay_ms=0):
                started = time.perf_counter()
                result = await session.call_tool(
                    "echo_probe",
                    {"marker": marker, "delay_ms": delay_ms},
                    read_timeout_seconds=timedelta(seconds=5),
                )
                data = result.structuredContent or {}
                row = {
                    "marker": marker,
                    "returned": data.get("marker"),
                    "delay_ms": delay_ms,
                    "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                    "ok": not result.isError and data.get("marker") == marker,
                }
                if marker.startswith("par-"):
                    order.append(marker)
                if not row["ok"]:
                    row["raw_result"] = result.model_dump(mode="json")
                show(row)
                return row

            warmup = await probe("warmup")
            if not warmup["ok"]:
                raise RuntimeError("warmup failed; inspect raw_result")
            sequential = [await probe(f"seq-{i}") for i in range(1, 11)]
            started = time.perf_counter()
            parallel = await asyncio.gather(
                probe("par-A", 900), probe("par-B", 100), probe("par-C", 500)
            )
            group_ms = round((time.perf_counter() - started) * 1000, 3)
            times = [r["elapsed_ms"] for r in sequential]
            show({
                "kind": "summary",
                "sequential_count": len(sequential),
                "sequential_min_ms": min(times),
                "sequential_median_ms": statistics.median(times),
                "sequential_max_ms": max(times),
                "concurrent_count": len(parallel),
                "concurrent_group_ms": group_ms,
                "completion_order": order,
                "failed_checks": sum(not r["ok"] for r in sequential + parallel),
            })


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("用法：python probes/mcp_load_probe.py /绝对路径/demos/mcp_side_effect_demo.py")
    asyncio.run(main())