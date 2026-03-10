"""Tests for src/auth.py."""

from unittest.mock import patch

import pytest

from src.auth import AUTH_LEVEL, require_write_access


class TestRequireWriteAccess:
    def test_raises_when_auth_level_is_none(self):
        token = AUTH_LEVEL.set("none")
        try:
            with pytest.raises(PermissionError, match="Write access denied"):
                require_write_access()
        finally:
            AUTH_LEVEL.reset(token)

    def test_raises_when_auth_level_is_read(self):
        token = AUTH_LEVEL.set("read")
        try:
            with pytest.raises(PermissionError, match="MCP_WRITE_TOKEN"):
                require_write_access()
        finally:
            AUTH_LEVEL.reset(token)

    def test_succeeds_when_auth_level_is_write(self):
        token = AUTH_LEVEL.set("write")
        try:
            require_write_access()  # Should not raise
        finally:
            AUTH_LEVEL.reset(token)

    def test_default_auth_level_is_none(self):
        # Default ContextVar value should be "none"
        assert AUTH_LEVEL.get() == "none"


class TestTokenConstants:
    def test_read_token_from_env(self, monkeypatch):
        monkeypatch.setenv("MCP_API_TOKEN", "test-read-token")
        # Re-import to pick up new env var
        import importlib
        import src.auth

        importlib.reload(src.auth)
        assert src.auth.READ_TOKEN == "test-read-token"

    def test_write_token_from_env(self, monkeypatch):
        monkeypatch.setenv("MCP_WRITE_TOKEN", "test-write-token")
        import importlib
        import src.auth

        importlib.reload(src.auth)
        assert src.auth.WRITE_TOKEN == "test-write-token"

    def test_tokens_none_when_unset(self, monkeypatch):
        monkeypatch.delenv("MCP_API_TOKEN", raising=False)
        monkeypatch.delenv("MCP_WRITE_TOKEN", raising=False)
        import importlib
        import src.auth

        importlib.reload(src.auth)
        assert src.auth.READ_TOKEN is None
        assert src.auth.WRITE_TOKEN is None
