"""Pardot / Account Engagement write MCP tool definitions."""

from src.auth import require_write_access
from src.pardot_client import (
    create_custom_field,
    create_email,
    create_email_template,
    create_list,
    create_list_email,
    create_list_membership,
    create_prospect,
    create_tag,
    delete_custom_field,
    delete_email_template,
    delete_list,
    delete_list_membership,
    delete_prospect,
    delete_tag,
    undelete_prospect,
    update_custom_field,
    update_email_template,
    update_list,
    update_list_membership,
    update_prospect,
    update_tag,
    upsert_prospect_by_email,
)


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
    def pardot_delete_prospect(prospect_id: str) -> dict:
        """Delete a Pardot prospect by ID.

        Args:
            prospect_id: The Pardot prospect ID to delete.

        Returns:
            A success dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return delete_prospect(prospect_id)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_upsert_prospect(data: dict) -> dict:
        """Upsert a Pardot prospect by email address.

        Creates a new prospect if no match exists, or updates the most recent
        prospect with that email. The data dict must include an 'email' field.

        Args:
            data: Dict of prospect fields (must include 'email', plus any other fields).

        Returns:
            The created or updated prospect as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return upsert_prospect_by_email(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_undelete_prospect(prospect_id: str) -> dict:
        """Restore a previously deleted Pardot prospect.

        Args:
            prospect_id: The Pardot prospect ID to restore.

        Returns:
            The restored prospect as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return undelete_prospect(prospect_id)
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

    @mcp.tool()
    def pardot_update_email_template(template_id: str, data: dict) -> dict:
        """Update an existing Pardot email template.

        Args:
            template_id: The email template ID to update.
            data: Dict of fields to update (e.g. name, subject, htmlMessage).

        Returns:
            The updated email template as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return update_email_template(template_id, data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_delete_email_template(template_id: str) -> dict:
        """Delete a Pardot email template by ID.

        Args:
            template_id: The email template ID to delete.

        Returns:
            A success dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return delete_email_template(template_id)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    # --- List Write ---

    @mcp.tool()
    def pardot_create_list(data: dict) -> dict:
        """Create a new Pardot static list.

        Args:
            data: Dict of list fields (e.g. name, title, description).

        Returns:
            The created list as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return create_list(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_update_list(list_id: str, data: dict) -> dict:
        """Update an existing Pardot static list.

        Args:
            list_id: The Pardot list ID to update.
            data: Dict of fields to update (e.g. name, title, description).

        Returns:
            The updated list as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return update_list(list_id, data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_delete_list(list_id: str) -> dict:
        """Delete a Pardot static list by ID.

        Args:
            list_id: The Pardot list ID to delete.

        Returns:
            A success dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return delete_list(list_id)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    # --- List Membership Write ---

    @mcp.tool()
    def pardot_create_list_membership(data: dict) -> dict:
        """Add a prospect to a Pardot list.

        Args:
            data: Dict with listId and prospectId (required).

        Returns:
            The created membership as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return create_list_membership(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_update_list_membership(membership_id: str, data: dict) -> dict:
        """Update an existing Pardot list membership.

        Args:
            membership_id: The list membership ID to update.
            data: Dict of fields to update (e.g. optedOut).

        Returns:
            The updated membership as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return update_list_membership(membership_id, data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_delete_list_membership(membership_id: str) -> dict:
        """Remove a prospect from a Pardot list.

        Args:
            membership_id: The list membership ID to delete.

        Returns:
            A success dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return delete_list_membership(membership_id)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    # --- Email Write ---

    @mcp.tool()
    def pardot_create_email(data: dict) -> dict:
        """Send a one-to-one Pardot email to a single prospect.

        Args:
            data: Dict with prospectId, emailTemplateId, campaignId, and optional fields.

        Returns:
            The created email as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return create_email(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_create_list_email(data: dict) -> dict:
        """Send a Pardot email to a list of prospects.

        Args:
            data: Dict with name, listId, emailTemplateId, campaignId, and optional fields.

        Returns:
            The created list email as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return create_list_email(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    # --- Custom Field Write ---

    @mcp.tool()
    def pardot_create_custom_field(data: dict) -> dict:
        """Create a new Pardot custom field.

        Args:
            data: Dict of custom field properties (e.g. name, fieldId, type).

        Returns:
            The created custom field as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return create_custom_field(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_update_custom_field(field_id: str, data: dict) -> dict:
        """Update an existing Pardot custom field.

        Args:
            field_id: The custom field ID to update.
            data: Dict of fields to update.

        Returns:
            The updated custom field as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return update_custom_field(field_id, data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_delete_custom_field(field_id: str) -> dict:
        """Delete a Pardot custom field by ID.

        Args:
            field_id: The custom field ID to delete.

        Returns:
            A success dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return delete_custom_field(field_id)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    # --- Tag Write ---

    @mcp.tool()
    def pardot_create_tag(data: dict) -> dict:
        """Create a new Pardot tag.

        Args:
            data: Dict with tag properties (e.g. name).

        Returns:
            The created tag as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return create_tag(data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_update_tag(tag_id: str, data: dict) -> dict:
        """Update an existing Pardot tag.

        Args:
            tag_id: The tag ID to update.
            data: Dict of fields to update (e.g. name).

        Returns:
            The updated tag as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return update_tag(tag_id, data)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_delete_tag(tag_id: str) -> dict:
        """Delete a Pardot tag by ID.

        Args:
            tag_id: The tag ID to delete.

        Returns:
            A success dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return delete_tag(tag_id)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}
