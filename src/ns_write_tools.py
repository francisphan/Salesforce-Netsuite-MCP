"""NetSuite write MCP tool definitions."""

from src.auth import require_write_access
from src.ns_client import rest_create, rest_delete, rest_update, rest_upsert


def register_tools(mcp):
    """Register all NetSuite write tools on the given FastMCP instance."""

    @mcp.tool()
    def ns_create_record(record_type: str, body: dict) -> dict:
        """Create a new NetSuite record via the REST API.

        Args:
            record_type: REST record type name (e.g. "customer", "salesOrder", "invoice").
            body: A dict of field name → value pairs for the new record.

        Returns:
            The created record as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return rest_create(record_type, body)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ns_update_record(record_type: str, record_id: str, body: dict) -> dict:
        """Update an existing NetSuite record by its type and internal ID.

        Args:
            record_type: REST record type name (e.g. "customer", "salesOrder", "invoice").
            record_id: The internal ID of the record to update.
            body: A dict of field name → value pairs to update.

        Returns:
            The updated record as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return rest_update(record_type, record_id, body)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ns_upsert_record(record_type: str, body: dict, external_id: str) -> dict:
        """Upsert a NetSuite record using an external ID.

        If a record with the given external ID exists, it is updated; otherwise a new
        record is created.

        Args:
            record_type: REST record type name (e.g. "customer", "salesOrder", "invoice").
            body: A dict of field name → value pairs for the record.
            external_id: The external ID value used to match an existing record.

        Returns:
            The upserted record as a dict, or an error dict on failure.
        """
        try:
            require_write_access()
            return rest_upsert(record_type, body, external_id)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ns_delete_record(record_type: str, record_id: str) -> dict:
        """Delete a NetSuite record by its type and internal ID.

        Args:
            record_type: REST record type name (e.g. "customer", "salesOrder", "invoice").
            record_id: The internal ID of the record to delete.

        Returns:
            A success confirmation dict, or an error dict on failure.
        """
        try:
            require_write_access()
            rest_delete(record_type, record_id)
            return {"success": True, "record_type": record_type, "record_id": record_id}
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}
