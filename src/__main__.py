"""Allow running as `python -m src`."""

from src.server import mcp

import os

transport = os.getenv("MCP_TRANSPORT", "sse")
mcp.run(transport=transport)
