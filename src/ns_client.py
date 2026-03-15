"""NetSuite client with TBA auth, singleton connection, and convenience wrappers."""

import os

from dotenv import load_dotenv

from src.netsuite import NetSuiteClient, NetSuiteConfig, TBAConfig

load_dotenv()

_ns_holder: list[NetSuiteClient | None] = [None]


def get_client() -> NetSuiteClient:
    """Return a configured NetSuiteClient instance (singleton)."""
    if _ns_holder[0] is None:
        config = NetSuiteConfig(
            account_id=os.environ["NETSUITE_ACCOUNT_ID"],
            tba=TBAConfig(
                consumer_key=os.environ["NETSUITE_TBA__CONSUMER_KEY"],
                consumer_secret=os.environ["NETSUITE_TBA__CONSUMER_SECRET"],
                token_key=os.environ["NETSUITE_TBA__TOKEN_KEY"],
                token_secret=os.environ["NETSUITE_TBA__TOKEN_SECRET"],
            ),
        )
        _ns_holder[0] = NetSuiteClient(config)
    return _ns_holder[0]


def suiteql_query(query: str, limit: int = 1000) -> list[dict]:
    """Execute a SuiteQL query and return all result items."""
    client = get_client()
    return list(client.suiteql.query_all(query, limit=limit))


def suiteql_query_page(query: str, limit: int = 1000, offset: int = 0) -> dict:
    """Execute a SuiteQL query and return a single page of results."""
    client = get_client()
    result = client.suiteql.query(query, limit=limit, offset=offset)
    return result.model_dump(by_alias=True)


def rest_get(
    record_type: str,
    record_id: str,
    *,
    expand_sub_resources: bool = False,
    fields: list[str] | None = None,
) -> dict:
    """Get a single NetSuite record by type and ID."""
    client = get_client()
    return client.rest.get(
        record_type,
        record_id,
        expand_sub_resources=expand_sub_resources,
        fields=fields,
    )


def rest_list(
    record_type: str,
    *,
    limit: int = 100,
    offset: int = 0,
    q: str | None = None,
) -> dict:
    """List NetSuite records of a given type."""
    client = get_client()
    result = client.rest.list(record_type, limit=limit, offset=offset, q=q)
    return result.model_dump()


def list_record_types() -> dict:
    """List available NetSuite record types."""
    client = get_client()
    return client.metadata.list_record_types()


def get_record_schema(record_type: str) -> dict:
    """Get field schema for a NetSuite record type."""
    client = get_client()
    return client.metadata.get_record_schema(record_type)


def rest_create(record_type: str, body: dict) -> dict:
    """Create a new NetSuite record."""
    client = get_client()
    return client.rest.create(record_type, body)


def rest_update(record_type: str, record_id: str, body: dict) -> dict:
    """Update an existing NetSuite record."""
    client = get_client()
    return client.rest.update(record_type, record_id, body)


def rest_upsert(record_type: str, body: dict, external_id: str) -> dict:
    """Upsert a NetSuite record using an external ID."""
    client = get_client()
    return client.rest.upsert(record_type, body, external_id=external_id)


def rest_delete(record_type: str, record_id: str) -> None:
    """Delete a NetSuite record."""
    client = get_client()
    client.rest.delete(record_type, record_id)
