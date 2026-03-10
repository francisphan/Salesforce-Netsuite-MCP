"""Allow running as `python -m src`."""

import os

import uvicorn

from src.auth import READ_TOKEN, WRITE_TOKEN
from src.server import BearerAuthMiddleware, mcp

transport = os.getenv("MCP_TRANSPORT", "streamable-http")
app = mcp.streamable_http_app() if transport == "streamable-http" else mcp.sse_app()

if READ_TOKEN or WRITE_TOKEN:
    app.add_middleware(BearerAuthMiddleware)

uvicorn.run(
    app,
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)
