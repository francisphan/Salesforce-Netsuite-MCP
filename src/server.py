"""MCP server entrypoint for Salesforce & NetSuite tools."""

import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(
    "Salesforce & NetSuite",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)

from src.sf_tools import register_tools as register_sf_tools  # noqa: E402
from src.ns_tools import register_tools as register_ns_tools  # noqa: E402

register_sf_tools(mcp)
register_ns_tools(mcp)

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "sse")
    mcp.run(transport=transport)
