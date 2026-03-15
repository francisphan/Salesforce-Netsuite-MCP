"""Pardot / Account Engagement write MCP tool definitions."""

from src.auth import require_write_access
from src.pardot_client import create_prospect, update_prospect, create_email_template


def register_tools(mcp):
    """Register all Pardot write tools on the given FastMCP instance."""

    @mcp.tool()
    def pardot_create_prospect(data: dict) -> dict:
        """Create a new Pardot prospect.

        Args:
            data: Dict of prospect fields (e.g. email, firstName, lastName, company).

        Returns:
            The created prospect as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return create_prospect(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_update_prospect(prospect_id: str, data: dict) -> dict:
        """Update an existing Pardot prospect by ID.

        Args:
            prospect_id: The Pardot prospect ID to update.
            data: Dict of fields to update (e.g. firstName, lastName, company).

        Returns:
            The updated prospect as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return update_prospect(prospect_id, data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_create_email_template(data: dict) -> dict:
        """Create a new Pardot email template.

        Args:
            data: Dict of email template fields (e.g. name, subject, htmlMessage, textMessage, folderId).

        Returns:
            The created email template as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return create_email_template(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}
