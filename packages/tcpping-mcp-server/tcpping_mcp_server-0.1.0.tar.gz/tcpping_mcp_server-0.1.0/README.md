# tcpping MCP stdio server (FastMCP)

FastMCP-based stdio MCP server implemented in `modern_server.py`. The earlier hand-written JSON-RPC variant has been removed for simplicity.

## Features
- Self-contained scraping core (`tcpping_core.py`)
- Single tool `tcpping_run` with rich parameters
- Fallback parsing & diagnostics (`debug` dumps HTML + screenshot)
- Optional `summary_only` mode for lightweight responses

## Run (from source checkout)
```bash
python -m tcpping.mcp.stdio.modern_server
```

## Run (after pip install)
```bash
tcpping-mcp
```

Both start a stdio MCP server exposing tool name `tcpping_run`.

Self-contained: the server embeds its own scraping core (`tcpping_core.py`) and does not import the top-level `run_tcpping.py`, making it easy to vendor just this directory.

### Invoke (conceptual example)
MCP client request (pseudo):
```json
{"jsonrpc":"2.0","id":"10","method":"tools/call","params":{"name":"tcpping_run","arguments":{"target":"admin.exchange.microsoft.com","summary_only":true}}}
```
Response result will be a JSON string (already serialized) containing either full dataset or minimal subset.

### FastMCP Tool Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| target | string | (required) | Domain or URL |
| port | int | 443 | TCP port |
| timeout | float | 120 | Max seconds overall |
| retries | int | 1 | Retry attempts |
| headless | bool | true | Headless browser mode |
| browser_channel | string | msedge | Playwright browser channel |
| debug | bool | false | Dump diagnostics on empty results |
| summary_only | bool | false | Return reduced summary subset |

### Returned Value
Serialized JSON string. Client may need to parse it once more to treat as object.

## Notes
- Ensure Playwright browsers installed:
```bash
pip install -r tcpping/requirements.txt
playwright install chromium
```
- If site structure changes, underlying `run_tcpping.py` improvements automatically propagate here.

## CLI Help (future)
The current entry point simply launches the MCP server. A future version may add flags like `--info` or `--version`.
