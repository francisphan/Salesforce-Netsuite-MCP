"""Authorization context for distinguishing read-only vs read-write access.

The BearerAuthMiddleware sets the auth level per-request using a ContextVar.
Write tools check `require_write_access()` before executing mutations.
"""

import os
from contextvars import ContextVar

AUTH_LEVEL: ContextVar[str] = ContextVar("auth_level", default="none")

# Token constants — loaded once at import time
READ_TOKEN = os.getenv("MCP_API_TOKEN")
WRITE_TOKEN = os.getenv("MCP_WRITE_TOKEN")


def require_write_access() -> None:
    """Raise if the current request does not have write-level authorization.

    Call this at the top of every write tool to gate mutations behind
    the MCP_WRITE_TOKEN.
    """
    level = AUTH_LEVEL.get()
    if level != "write":
        raise PermissionError(
            "Write access denied. This operation requires the MCP_WRITE_TOKEN. "
            "Pass it as a Bearer token in the Authorization header."
        )
