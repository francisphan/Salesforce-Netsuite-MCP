"""Salesforce MCP tool definitions."""

from src.sf_client import describe_object, get_record, list_objects, query


def register_tools(mcp):
    """Register all Salesforce tools on the given FastMCP instance."""

    @mcp.tool()
    def sf_soql_query(query_str: str) -> list[dict]:
        """Execute a SOQL query against Salesforce and return matching records.

        Args:
            query_str: A valid SOQL query string (e.g. "SELECT Id, Name FROM Account LIMIT 10").

        Returns:
            A list of record dicts, or a single-element list with an error dict on failure.
        """
        try:
            return query(query_str)
        except Exception as e:
            return [{"error": str(e)}]

    @mcp.tool()
    def sf_describe_object(object_name: str) -> dict:
        """Describe a Salesforce object's metadata including fields, relationships, and properties.

        Args:
            object_name: API name of the SObject (e.g. "Account", "TVRS_Guest__c").

        Returns:
            Object metadata dict, or an error dict on failure.
        """
        try:
            return describe_object(object_name)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def sf_list_objects() -> list[str]:
        """List all queryable Salesforce object API names, sorted alphabetically.

        Returns:
            A sorted list of object names, or a single-element list with an error dict on failure.
        """
        try:
            return list_objects()
        except Exception as e:
            return [{"error": str(e)}]

    @mcp.tool()
    def sf_get_record(object_name: str, record_id: str) -> dict:
        """Get a single Salesforce record by its object type and record ID.

        Args:
            object_name: API name of the SObject (e.g. "Account", "TVRS_Guest__c").
            record_id: The 15 or 18-character Salesforce record ID.

        Returns:
            The record as a dict, or an error dict on failure.
        """
        try:
            return get_record(object_name, record_id)
        except Exception as e:
            return {"error": str(e)}
