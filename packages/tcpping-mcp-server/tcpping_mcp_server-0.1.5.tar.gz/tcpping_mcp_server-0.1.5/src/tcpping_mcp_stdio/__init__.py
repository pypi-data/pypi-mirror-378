"""TCP Ping MCP Server package."""
from .modern_server import mcp, main, VERSION as __version__
from .tcpping_core import run_test
__all__ = ["mcp", "run_test", "main", "__version__"]
