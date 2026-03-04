"""Salesforce MCP tool definitions."""

from src.sf_client import describe_object, get_record, list_objects, query
from src.sf_schema import SCHEMA, OBJECT_NAMES


def register_tools(mcp):
    """Register all Salesforce tools on the given FastMCP instance."""

    @mcp.tool()
    def sf_soql_query(query_str: str) -> list[dict]:
        """Execute a SOQL query against Salesforce and return matching records.

        Core objects: TVRS_Guest__c (guest reservations, external ID: Email__c),
        Account (Person Accounts), Contact, Opportunity, Lead, Campaign, CampaignMember, Task.

        Key relationships: TVRS_Guest__c.Contact__c -> Contact -> Account (via AccountId).
        Opportunity.AccountId -> Account. CampaignMember links Contact/Lead to Campaign.

        Use sf_get_schema to explore field names, relationships, and example SOQL before querying.

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

    @mcp.tool()
    def sf_get_schema(objects: str = "") -> dict:
        """Return curated schema for Salesforce objects including fields, relationships, and example SOQL.

        Call this before writing SOQL queries to discover field names, relationships, and query patterns.

        Args:
            objects: Comma-separated list of object API names (e.g. "Account,TVRS_Guest__c").
                     If empty, returns schema for all curated objects.

        Returns:
            A dict keyed by object name with field, relationship, and example query info.
            Unknown objects are silently omitted. Returns an error dict on complete failure.
        """
        if not objects.strip():
            return SCHEMA

        result = {}
        for obj_name in objects.split(","):
            obj_name = obj_name.strip()
            if not obj_name:
                continue
            # Case-insensitive lookup
            for schema_name, schema_data in SCHEMA.items():
                if schema_name.lower() == obj_name.lower():
                    result[schema_name] = schema_data
                    break

        return result
