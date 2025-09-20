"""Modern FastMCP-based TCP ping server using the latest FastMCP framework.

This module exposes a FastMCP server instance plus a CLI entry point `main()`
so that the package can install a console script on PyPI. The previous
console script mapping pointed directly at the `mcp` object; some tooling
expects a callable, so we provide an explicit wrapper.
"""

from fastmcp import FastMCP
from tcpping_core import run_test
import json
from typing import Optional

# Create FastMCP server instance
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
    """Run TCP ping test via pingloc.com and return structured JSON.

    Args:
        target: Domain or URL (scheme optional)
        port: TCP port (default 443)
        timeout: Overall max wait seconds
        retries: Retry attempts on failure
        headless: Run browser headless (default True)
        browser_channel: Playwright channel (msedge/chrome/...)
        debug: Dump diagnostics on empty probes
        summary_only: Return only summary subset if True
        
    Returns:
        JSON string with ping results or summary
    """
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

VERSION = "0.1.1"  # Keep in sync with pyproject.toml and __init__.__version__

# Optional: Add a resource for server information
@mcp.resource("tcpping://info")
def get_server_info() -> dict:
    """Get information about the TCP ping server."""
    return {
        "name": "TCP Ping MCP Server",
        "version": VERSION, 
        "description": "Provides TCP connectivity testing via pingloc.com",
        "supported_channels": ["msedge", "chrome", "chromium"],
        "default_port": 443,
        "default_timeout": 120
    }

def main() -> None:
    """CLI entry point that runs the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()