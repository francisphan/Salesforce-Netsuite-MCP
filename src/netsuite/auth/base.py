"""Base auth class for NetSuite."""

from __future__ import annotations

import httpx


class NetSuiteAuth(httpx.Auth):
    """Abstract base for NetSuite auth providers."""
