"""Tests for src/pardot_write_tools.py."""

from unittest.mock import MagicMock, patch

import pytest

from src.pardot_write_tools import register_tools


@pytest.fixture
def mcp_with_tools():
    """Create a mock MCP instance and register Pardot write tools on it."""
    mcp = MagicMock()
    registered = {}

    def tool_decorator():
        def wrapper(func):
            registered[func.__name__] = func
            return func
        return wrapper

    mcp.tool = tool_decorator
    register_tools(mcp)
    return registered


class TestToolRegistration:
    def test_all_tools_registered(self, mcp_with_tools):
        expected = {
            "pardot_create_prospect",
            "pardot_update_prospect",
        }
        assert set(mcp_with_tools.keys()) == expected


class TestPardotCreateProspect:
    @patch("src.pardot_write_tools.create_prospect")
    @patch("src.pardot_write_tools.require_write_access")
    def test_success(self, mock_auth, mock_create, mcp_with_tools):
        mock_create.return_value = {"id": "100", "email": "new@test.com"}
        result = mcp_with_tools["pardot_create_prospect"](
            {"email": "new@test.com", "firstName": "Jane", "lastName": "Doe"}
        )
        mock_auth.assert_called_once()
        mock_create.assert_called_once_with(
            {"email": "new@test.com", "firstName": "Jane", "lastName": "Doe"}
        )
        assert result["id"] == "100"

    @patch("src.pardot_write_tools.require_write_access")
    def test_permission_denied(self, mock_auth, mcp_with_tools):
        mock_auth.side_effect = PermissionError("Write access denied")
        result = mcp_with_tools["pardot_create_prospect"]({"email": "a@b.com"})
        assert result == {"error": "Write access denied"}

    @patch("src.pardot_write_tools.create_prospect")
    @patch("src.pardot_write_tools.require_write_access")
    def test_api_error(self, mock_auth, mock_create, mcp_with_tools):
        mock_create.side_effect = Exception("Email already exists")
        result = mcp_with_tools["pardot_create_prospect"]({"email": "dup@test.com"})
        assert result == {"error": "Email already exists"}


class TestPardotUpdateProspect:
    @patch("src.pardot_write_tools.update_prospect")
    @patch("src.pardot_write_tools.require_write_access")
    def test_success(self, mock_auth, mock_update, mcp_with_tools):
        mock_update.return_value = {"id": "100", "firstName": "Updated"}
        result = mcp_with_tools["pardot_update_prospect"](
            "100", {"firstName": "Updated"}
        )
        mock_auth.assert_called_once()
        mock_update.assert_called_once_with("100", {"firstName": "Updated"})
        assert result["firstName"] == "Updated"

    @patch("src.pardot_write_tools.require_write_access")
    def test_permission_denied(self, mock_auth, mcp_with_tools):
        mock_auth.side_effect = PermissionError("Write access denied")
        result = mcp_with_tools["pardot_update_prospect"]("100", {"firstName": "X"})
        assert result == {"error": "Write access denied"}

    @patch("src.pardot_write_tools.update_prospect")
    @patch("src.pardot_write_tools.require_write_access")
    def test_api_error(self, mock_auth, mock_update, mcp_with_tools):
        mock_update.side_effect = Exception("Prospect not found")
        result = mcp_with_tools["pardot_update_prospect"]("999", {"firstName": "X"})
        assert result == {"error": "Prospect not found"}
