"""Salesforce MCP tool definitions."""

from src.sf_client import (
    get_record, query, query_page,
    search, quick_search, get_limits, get_recent_items,
)
from src.schema_cache import schema_cache
from src.sf_schema import SCHEMA, OBJECT_NAMES
from src.query_validator import validate_soql, enhance_sf_error


def register_tools(mcp):
    """Register all Salesforce tools on the given FastMCP instance."""

    @mcp.tool()
    def sf_soql_query(
        query_str: str = "", next_records_url: str = ""
    ) -> list[dict] | dict:
        """Execute a SOQL query against Salesforce and return matching records.

        Core objects: TVRS_Guest__c (guest reservations, external ID: Email__c),
        Account (Person Accounts), Contact, Opportunity, Lead, Campaign, CampaignMember, Task.

        Key relationships: TVRS_Guest__c.Contact__c -> Contact -> Account (via AccountId).
        Opportunity.AccountId -> Account. CampaignMember links Contact/Lead to Campaign.

        Use sf_get_schema to explore field names, relationships, and example SOQL before querying.

        Pagination: By default, all matching records are returned. For large result sets,
        pass next_records_url (returned as 'nextRecordsUrl' in previous response) to fetch
        the next page instead.

        Args:
            query_str: A valid SOQL query string (e.g. "SELECT Id, Name FROM Account LIMIT 10").
                       Required for the initial query; omit when using next_records_url.
            next_records_url: URL from a previous response's 'nextRecordsUrl' to fetch the next page.
                              When provided, query_str is ignored.

        Returns:
            If next_records_url is provided: a dict with 'records', 'totalSize', 'done',
            and optionally 'nextRecordsUrl' for the next page.
            Otherwise: a list of all record dicts, or a dict with warnings/errors.
        """
        # Paginated follow-up — return a single page
        if next_records_url:
            try:
                return query_page(next_records_url=next_records_url)
            except Exception as e:
                return {"error": str(e)}

        if not query_str:
            return {"error": "Either query_str or next_records_url must be provided."}

        # Pre-flight validation
        validation = validate_soql(query_str)
        if not validation["valid"]:
            return {
                "validation_errors": validation["warnings"],
                "suggestions": validation["suggestions"],
                "note": "Query was NOT executed due to validation errors. Fix the issues above and retry.",
            }

        try:
            records = query(query_str)
            # Attach validation warnings if any
            if validation["warnings"]:
                return {
                    "records": records,
                    "warnings": validation["warnings"],
                    "suggestions": validation["suggestions"],
                }
            return records
        except Exception as e:
            enhanced = enhance_sf_error(str(e), query_str)
            return [{"error": enhanced}]

    @mcp.tool()
    def sf_describe_object(object_name: str) -> dict:
        """Describe a Salesforce object's metadata including fields, relationships, and properties.

        Results are cached and refreshed automatically in the background.

        Args:
            object_name: API name of the SObject (e.g. "Account", "TVRS_Guest__c").

        Returns:
            Object metadata dict, or an error dict on failure.
        """
        try:
            return schema_cache.sf_describe(object_name)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def sf_list_objects() -> list[str]:
        """List all queryable Salesforce object API names, sorted alphabetically.

        Results are cached and refreshed automatically in the background.

        Returns:
            A sorted list of object names, or a single-element list with an error dict on failure.
        """
        try:
            return schema_cache.sf_list_objects()
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

    @mcp.tool()
    def sf_search(sosl_query: str = "", search_term: str = "") -> list[dict] | dict:
        """Search across multiple Salesforce objects using SOSL (full-text search).

        Two modes:
        1. Full SOSL: Pass sosl_query with a complete SOSL query string
           (e.g. "FIND {John Smith} IN ALL FIELDS RETURNING Contact, Lead, Account")
        2. Quick search: Pass search_term for a simple cross-object text search.

        Use this instead of sf_soql_query when you don't know which object contains
        the data, or need to search across multiple objects simultaneously.

        Args:
            sosl_query: Full SOSL query string. Takes precedence if both provided.
            search_term: Simple search string for quick cross-object search.

        Returns:
            A list of matching record dicts, or an error dict on failure.
        """
        if not sosl_query and not search_term:
            return {"error": "Provide either sosl_query or search_term."}
        try:
            if sosl_query:
                return search(sosl_query)
            return quick_search(search_term)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def sf_get_limits() -> dict:
        """Return current Salesforce API usage and org limits.

        Shows daily API call counts, remaining quota, data storage, and other
        org limits. No parameters needed. Useful for monitoring API consumption
        before running bulk operations.

        Returns:
            A dict of limit names to their Max/Remaining values.
        """
        try:
            return get_limits()
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def sf_recent_items(limit: int = 20) -> list[dict] | dict:
        """Return recently viewed/accessed Salesforce records for the connected user.

        Useful for understanding what the current user has been working on
        or for quickly accessing recently viewed records.

        Args:
            limit: Maximum number of recent items to return (default 20, max 200).

        Returns:
            A list of recently viewed record dicts, or an error dict on failure.
        """
        try:
            capped = min(max(limit, 1), 200)
            return get_recent_items(capped)
        except Exception as e:
            return {"error": str(e)}
