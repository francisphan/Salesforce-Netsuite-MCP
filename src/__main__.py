"""Allow running as `python -m src`."""

import os

import uvicorn

from src.server import API_TOKEN, BearerAuthMiddleware, mcp

transport = os.getenv("MCP_TRANSPORT", "streamable-http")
app = mcp.streamable_http_app() if transport == "streamable-http" else mcp.sse_app()

if API_TOKEN:
    app.add_middleware(BearerAuthMiddleware)

uvicorn.run(
    app,
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)
