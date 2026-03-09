"""MCP server entrypoint for Salesforce & NetSuite tools."""

import json
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

load_dotenv()

API_TOKEN = os.getenv("MCP_API_TOKEN")


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not API_TOKEN:
            return await call_next(request)
        if request.url.path == "/health":
            return await call_next(request)
        auth = request.headers.get("authorization", "")
        if auth != f"Bearer {API_TOKEN}":
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


mcp = FastMCP(
    "Salesforce, NetSuite & Pardot",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok"})


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
from src.sf_tools import register_tools as register_sf_tools  # noqa: E402
from src.ns_tools import register_tools as register_ns_tools  # noqa: E402
from src.pardot_tools import register_tools as register_pardot_tools  # noqa: E402
from src.cross_tools import register_tools as register_cross_tools  # noqa: E402

register_sf_tools(mcp)
register_ns_tools(mcp)
register_pardot_tools(mcp)
register_cross_tools(mcp)


# ---------------------------------------------------------------------------
# Resources — browsable context for AI clients
# ---------------------------------------------------------------------------
from src.sf_schema import SCHEMA as SF_SCHEMA  # noqa: E402
from src.ns_schema import SCHEMA as NS_SCHEMA  # noqa: E402


@mcp.resource("schema://salesforce")
def salesforce_schema_resource() -> str:
    """Complete curated Salesforce schema with fields, relationships, and example SOQL.

    Covers: TVRS_Guest__c, Account, Contact, Opportunity, Lead, Campaign, CampaignMember, Task.
    """
    return json.dumps(SF_SCHEMA, indent=2)


@mcp.resource("schema://netsuite")
def netsuite_schema_resource() -> str:
    """Complete curated NetSuite schema with fields, SuiteQL tables, and example queries.

    Covers: customer, salesOrder, invoice, item, transaction, vendor, employee, contact.
    """
    return json.dumps(NS_SCHEMA, indent=2)


@mcp.resource("schema://salesforce/{object_name}")
def salesforce_object_resource(object_name: str) -> str:
    """Schema for a specific Salesforce object (e.g. schema://salesforce/TVRS_Guest__c)."""
    for name, schema in SF_SCHEMA.items():
        if name.lower() == object_name.lower():
            return json.dumps({name: schema}, indent=2)
    return json.dumps({"error": f"Object '{object_name}' not found in curated schema."})


@mcp.resource("schema://netsuite/{record_type}")
def netsuite_record_resource(record_type: str) -> str:
    """Schema for a specific NetSuite record type (e.g. schema://netsuite/customer)."""
    for name, schema in NS_SCHEMA.items():
        if name.lower() == record_type.lower():
            return json.dumps({name: schema}, indent=2)
    return json.dumps({"error": f"Record type '{record_type}' not found in curated schema."})


@mcp.resource("guide://query-patterns")
def query_patterns_resource() -> str:
    """Common query patterns and tips for Salesforce SOQL and NetSuite SuiteQL."""
    return json.dumps({
        "soql_tips": [
            "Use sf_get_schema before writing SOQL to discover field names",
            "TVRS_Guest__c.Contact__r.AccountId traverses Guest -> Contact -> Account",
            "Person Accounts: query Account with IsPersonAccount = true, use PersonEmail",
            "Aggregate queries: SELECT StageName, COUNT(Id) FROM Opportunity GROUP BY StageName",
            "Date literals: TODAY, LAST_N_DAYS:30, THIS_YEAR, NEXT_WEEK",
            "Subqueries: SELECT Id, (SELECT Id FROM Contacts) FROM Account",
        ],
        "suiteql_tips": [
            "Use ns_get_netsuite_schema before writing SuiteQL to discover table/field names",
            "All transactions live in 'transaction' table — filter by type column",
            "Transaction type codes: SalesOrd, CustInvc, CustPymt, VendBill, PurchOrd, Journal",
            "Line items: JOIN transactionline tl ON t.id = tl.transaction",
            "Customer booleans: use 'T'/'F' strings, not true/false",
            "Date functions: TO_DATE('2025-01-01', 'YYYY-MM-DD'), SYSDATE",
            "Case-sensitive string compare — use LOWER() for case-insensitive matching",
        ],
        "cross_system": [
            "Use lookup_guest_by_email for quick cross-system existence checks",
            "Use guest_360_profile for a unified view with stay history + financials + marketing",
            "Email is the primary cross-system key (SF Email__c, NS email, Pardot email)",
        ],
    }, indent=2)


# ---------------------------------------------------------------------------
# Prompts — pre-built templates for common operations
# ---------------------------------------------------------------------------

@mcp.prompt()
def guest_arrivals() -> str:
    """Find all guests arriving this week with their details."""
    return (
        "Find all guests arriving this week at The Vines. "
        "First call sf_get_schema(objects='TVRS_Guest__c') to see the fields, "
        "then query: SELECT Id, Guest_First_Name__c, Guest_Last_Name__c, Email__c, "
        "Check_In_Date__c, Check_Out_Date__c, Villa_number__c, City__c, Country__c, "
        "Language__c, Comments__c FROM TVRS_Guest__c "
        "WHERE Check_In_Date__c = THIS_WEEK ORDER BY Check_In_Date__c ASC"
    )


@mcp.prompt()
def sales_pipeline() -> str:
    """Show current open opportunities grouped by stage."""
    return (
        "Show the current sales pipeline. Query open opportunities grouped by stage: "
        "SELECT StageName, COUNT(Id) cnt, SUM(Amount) total "
        "FROM Opportunity WHERE IsClosed = false "
        "GROUP BY StageName ORDER BY SUM(Amount) DESC. "
        "Then also get the top 10 open opportunities by amount: "
        "SELECT Id, Name, StageName, Amount, CloseDate, Owner.Name, Account.Name "
        "FROM Opportunity WHERE IsClosed = false ORDER BY Amount DESC LIMIT 10"
    )


@mcp.prompt()
def guest_lookup(email: str) -> str:
    """Look up a guest across all systems by email."""
    return (
        f"Look up the guest with email '{email}' across all systems. "
        f"Use the guest_360_profile tool to get their unified profile including "
        f"stay history, financial data, and marketing engagement."
    )


@mcp.prompt()
def netsuite_revenue() -> str:
    """Summarize recent NetSuite revenue by transaction type."""
    return (
        "Summarize recent NetSuite revenue. First call ns_get_netsuite_schema(record_types='transaction') "
        "to understand the table structure, then query: "
        "SELECT type, COUNT(*) AS cnt, SUM(foreigntotal) AS total "
        "FROM transaction "
        "WHERE trandate >= TO_DATE('2025-01-01', 'YYYY-MM-DD') "
        "GROUP BY type ORDER BY total DESC"
    )


@mcp.prompt()
def stale_opportunities() -> str:
    """Find stale opportunities that haven't been updated recently."""
    return (
        "Find stale opportunities — open deals that haven't been modified in 30+ days. "
        "Query: SELECT Id, Name, StageName, Amount, CloseDate, LastModifiedDate, "
        "Owner.Name, Account.Name FROM Opportunity "
        "WHERE IsClosed = false AND LastModifiedDate < LAST_N_DAYS:30 "
        "ORDER BY LastModifiedDate ASC LIMIT 20"
    )


@mcp.prompt()
def outstanding_invoices() -> str:
    """Find unpaid NetSuite invoices."""
    return (
        "Find outstanding (unpaid) NetSuite invoices. "
        "First check ns_get_netsuite_schema(record_types='invoice') for field names, then query: "
        "SELECT t.id, t.tranid, t.trandate, t.duedate, t.status, "
        "t.foreigntotal, t.foreignamountremaining, c.companyname, c.email "
        "FROM transaction t JOIN customer c ON t.entity = c.id "
        "WHERE t.type = 'CustInvc' AND t.foreignamountremaining > 0 "
        "ORDER BY t.duedate ASC"
    )


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    mcp.run(transport=transport)
