"""MCP server entrypoint for Salesforce & NetSuite tools."""

import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

load_dotenv()

API_TOKEN = os.getenv("MCP_API_TOKEN")


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not API_TOKEN:
            return await call_next(request)
        if request.url.path == "/health":
            return await call_next(request)
        auth = request.headers.get("authorization", "")
        if auth != f"Bearer {API_TOKEN}":
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


mcp = FastMCP(
    "Salesforce, NetSuite & Pardot",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok"})


from src.sf_tools import register_tools as register_sf_tools  # noqa: E402
from src.ns_tools import register_tools as register_ns_tools  # noqa: E402
from src.pardot_tools import register_tools as register_pardot_tools  # noqa: E402

register_sf_tools(mcp)
register_ns_tools(mcp)
register_pardot_tools(mcp)

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    mcp.run(transport=transport)
