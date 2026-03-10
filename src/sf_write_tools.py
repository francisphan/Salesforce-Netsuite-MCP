"""Salesforce write MCP tool definitions (create, update, delete, upsert)."""

from src.auth import require_write_access
from src.sf_client import create_record, update_record, delete_record, upsert_record


def register_tools(mcp):
    """Register all Salesforce write tools on the given FastMCP instance."""

    @mcp.tool()
    def sf_create_record(object_name: str, data: dict) -> dict:
        """Create a new Salesforce record.

        Args:
            object_name: API name of the SObject (e.g. "Account", "TVRS_Guest__c").
            data: A dict of field name -> value pairs to set on the new record.

        Returns:
            The creation result dict (includes id, success, errors), or an error dict on failure.
        """
        try:
            require_write_access()
        except PermissionError as e:
            return {"error": str(e)}
        try:
            return create_record(object_name, data)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def sf_update_record(object_name: str, record_id: str, data: dict) -> dict:
        """Update an existing Salesforce record by ID.

        Args:
            object_name: API name of the SObject (e.g. "Account", "TVRS_Guest__c").
            record_id: The 15 or 18-character Salesforce record ID.
            data: A dict of field name -> value pairs to update on the record.

        Returns:
            The update result dict, or an error dict on failure.
        """
        try:
            require_write_access()
        except PermissionError as e:
            return {"error": str(e)}
        try:
            return update_record(object_name, record_id, data)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def sf_delete_record(object_name: str, record_id: str) -> dict:
        """Delete a Salesforce record by ID.

        Args:
            object_name: API name of the SObject (e.g. "Account", "TVRS_Guest__c").
            record_id: The 15 or 18-character Salesforce record ID.

        Returns:
            The deletion result dict, or an error dict on failure.
        """
        try:
            require_write_access()
        except PermissionError as e:
            return {"error": str(e)}
        try:
            return delete_record(object_name, record_id)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def sf_upsert_record(
        object_name: str, external_id_field: str, external_id: str, data: dict
    ) -> dict:
        """Upsert a Salesforce record using an external ID field.

        Inserts a new record if no match is found for the external ID, or updates
        the existing record if a match exists.

        Args:
            object_name: API name of the SObject (e.g. "Account", "TVRS_Guest__c").
            external_id_field: API name of the external ID field (e.g. "Email__c").
            external_id: The external ID value to match on.
            data: A dict of field name -> value pairs to set on the record.

        Returns:
            The upsert result dict, or an error dict on failure.
        """
        try:
            require_write_access()
        except PermissionError as e:
            return {"error": str(e)}
        try:
            return upsert_record(object_name, external_id_field, external_id, data)
        except Exception as e:
            return {"error": str(e)}
