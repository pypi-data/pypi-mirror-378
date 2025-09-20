"""Modern FastMCP-based TCP ping server using the latest FastMCP framework."""
from fastmcp import FastMCP
from .tcpping_core import run_test
import json

mcp = FastMCP("tcpping-server")

@mcp.tool
async def tcpping_run(
    target: str,
    port: int = 443,
    timeout: float = 120,
    retries: int = 1,
    headless: bool = True,
    browser_channel: str = "msedge",
    debug: bool = False,
    summary_only: bool = False,
) -> str:
    data = await run_test(
        target=target,
        port=port,
        timeout=timeout,
        headless=headless,
        retries=retries,
        browser_channel=browser_channel,
        debug=debug,
    )
    if summary_only:
        minimal = {
            "host": data.get("host"),
            "generated_at": data.get("generated_at"),
            "summary": data.get("summary"),
            "probe_count": data.get("probe_count"),
            "timeouts": data.get("timeouts"),
            "duration_sec": data.get("duration_sec"),
        }
        return json.dumps(minimal, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)

VERSION = "0.1.4"

@mcp.resource("tcpping://info")
def get_server_info() -> dict:
    return {
        "name": "TCP Ping MCP Server",
        "version": VERSION,
        "description": "Provides TCP connectivity testing via pingloc.com",
        "supported_channels": ["msedge", "chrome", "chromium"],
        "default_port": 443,
        "default_timeout": 120,
    }

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()
