"""NetSuite MCP tool definitions."""

from src.ns_client import (
    get_record_schema,
    list_record_types,
    rest_get,
    rest_list,
    suiteql_query,
)


def register_tools(mcp):
    """Register all NetSuite tools on the given FastMCP instance."""

    @mcp.tool()
    def ns_suiteql_query(query: str, limit: int = 1000) -> list[dict]:
        """Execute a SuiteQL query against NetSuite and return matching records.

        Args:
            query: A valid SuiteQL query string (e.g. "SELECT id, companyname FROM customer").
            limit: Max rows per page (default 1000). All pages are fetched automatically.

        Returns:
            A list of result dicts, or a single-element list with an error dict on failure.
        """
        try:
            return suiteql_query(query, limit=limit)
        except Exception as e:
            return [{"error": str(e)}]

    @mcp.tool()
    def ns_rest_get(
        record_type: str, record_id: str, expand_sub_resources: bool = False
    ) -> dict:
        """Get a single NetSuite record by its type and internal ID.

        Args:
            record_type: REST record type name (e.g. "customer", "salesOrder", "invoice").
            record_id: The internal ID of the record.
            expand_sub_resources: If True, include all sublists/subrecords in the response.

        Returns:
            The record as a dict, or an error dict on failure.
        """
        try:
            return rest_get(record_type, record_id, expand_sub_resources=expand_sub_resources)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ns_rest_list(
        record_type: str,
        limit: int = 100,
        offset: int = 0,
        q: str | None = None,
    ) -> dict:
        """List NetSuite records of a given type with optional filtering.

        Args:
            record_type: REST record type name (e.g. "customer", "salesOrder").
            limit: Maximum number of records to return (default 100).
            offset: Starting offset for pagination (default 0).
            q: Optional query filter string.

        Returns:
            A dict with items, count, hasMore, and pagination info, or an error dict on failure.
        """
        try:
            return rest_list(record_type, limit=limit, offset=offset, q=q)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ns_list_record_types() -> dict:
        """List all available NetSuite record types from the metadata catalog.

        Returns:
            A dict of record type metadata, or an error dict on failure.
        """
        try:
            return list_record_types()
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def ns_get_record_schema(record_type: str) -> dict:
        """Get the field schema for a NetSuite record type.

        Args:
            record_type: REST record type name (e.g. "customer", "salesOrder").

        Returns:
            A dict describing the record's fields and structure, or an error dict on failure.
        """
        try:
            return get_record_schema(record_type)
        except Exception as e:
            return {"error": str(e)}
