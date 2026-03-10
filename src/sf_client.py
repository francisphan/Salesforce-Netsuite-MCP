"""Salesforce client with OAuth refresh token auth, singleton connection, and retry logic."""

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceExpiredSession

load_dotenv()

TOKEN_CACHE = Path(__file__).parent.parent / ".token_cache.json"

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubled each retry

_sf_holder: list[Salesforce | None] = [None]


def _save_token(instance_url: str, access_token: str, refresh_token: str | None = None):
    cache = {"instance_url": instance_url, "access_token": access_token}
    if refresh_token:
        cache["refresh_token"] = refresh_token
    elif TOKEN_CACHE.exists():
        try:
            old = json.loads(TOKEN_CACHE.read_text())
            if old.get("refresh_token"):
                cache["refresh_token"] = old["refresh_token"]
        except Exception:
            pass
    TOKEN_CACHE.write_text(json.dumps(cache))


def _load_cached_token() -> Salesforce | None:
    """Try to connect using a cached token. Returns None if expired/missing."""
    if not TOKEN_CACHE.exists():
        return None
    try:
        data = json.loads(TOKEN_CACHE.read_text())
        sf = Salesforce(instance_url=data["instance_url"], session_id=data["access_token"])
        sf.describe()  # test if token is still valid
        return sf
    except Exception:
        return None


def _refresh_oauth_token() -> Salesforce | None:
    """Silently refresh the access token using the cached refresh token."""
    if not TOKEN_CACHE.exists():
        return None
    try:
        cache = json.loads(TOKEN_CACHE.read_text())
        refresh_token = cache.get("refresh_token")
        if not refresh_token:
            return None
    except Exception:
        return None

    client_id = os.environ["SF_CLIENT_ID"]
    client_secret = os.environ["SF_CLIENT_SECRET"]
    domain = os.environ.get("SF_DOMAIN") or "login"
    base_url = f"https://{domain}.salesforce.com"

    import requests

    resp = requests.post(
        f"{base_url}/services/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    if not resp.ok:
        return None

    data = resp.json()
    _save_token(data["instance_url"], data["access_token"], data.get("refresh_token"))
    return Salesforce(instance_url=data["instance_url"], session_id=data["access_token"])


def _refresh_from_env() -> Salesforce | None:
    """Refresh using SF_REFRESH_TOKEN env var (for deployed environments without token cache)."""
    refresh_token = os.environ.get("SF_REFRESH_TOKEN")
    if not refresh_token:
        return None

    client_id = os.environ["SF_CLIENT_ID"]
    client_secret = os.environ["SF_CLIENT_SECRET"]
    domain = os.environ.get("SF_DOMAIN") or "login"
    base_url = f"https://{domain}.salesforce.com"

    import requests

    resp = requests.post(
        f"{base_url}/services/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    if not resp.ok:
        return None

    data = resp.json()
    _save_token(data["instance_url"], data["access_token"], refresh_token)
    return Salesforce(instance_url=data["instance_url"], session_id=data["access_token"])


def _reconnect() -> Salesforce:
    """Re-authenticate using OAuth refresh token."""
    refreshed = _refresh_oauth_token()
    if refreshed:
        return refreshed
    refreshed = _refresh_from_env()
    if refreshed:
        return refreshed
    raise RuntimeError(
        "Salesforce OAuth refresh failed. Re-run the initial OAuth flow to get a new refresh token."
    )


def get_client() -> Salesforce:
    """Return a connected Salesforce instance (singleton — reconnects if needed)."""
    if _sf_holder[0] is None:
        cached = _load_cached_token()
        if cached:
            _sf_holder[0] = cached
        else:
            _sf_holder[0] = _reconnect()
    return _sf_holder[0]


def _with_retry(func):
    """Execute func(sf) with retry on transient errors and re-auth on expired session."""
    if _sf_holder[0] is None:
        get_client()
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            return func(_sf_holder[0])
        except SalesforceExpiredSession:
            _sf_holder[0] = _reconnect()
            continue
        except Exception as e:
            last_exc = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2**attempt))
            continue
    raise last_exc


def query(soql: str) -> list[dict]:
    """Run a SOQL query with automatic retry."""

    def _do(sf):
        result = sf.query_all(soql)
        records = result.get("records", [])
        for r in records:
            r.pop("attributes", None)
        return records

    return _with_retry(_do)


def describe_object(object_name: str) -> dict:
    """Describe a Salesforce object with retry."""

    def _do(sf):
        return getattr(sf, object_name).describe()

    return _with_retry(_do)


def list_objects() -> list[str]:
    """List all queryable SObject names, sorted."""

    def _do(sf):
        desc = sf.describe()
        return sorted(obj["name"] for obj in desc["sobjects"] if obj["queryable"])

    return _with_retry(_do)


def get_record(object_name: str, record_id: str) -> dict:
    """Get a single record by Id with retry."""

    def _do(sf):
        record = getattr(sf, object_name).get(record_id)
        record.pop("attributes", None)
        return record

    return _with_retry(_do)


def create_record(object_name: str, data: dict) -> dict:
    """Create a new Salesforce record with retry."""

    def _do(sf):
        return getattr(sf, object_name).create(data)

    return _with_retry(_do)


def update_record(object_name: str, record_id: str, data: dict) -> dict:
    """Update an existing Salesforce record by Id with retry."""

    def _do(sf):
        return getattr(sf, object_name).update(record_id, data)

    return _with_retry(_do)


def delete_record(object_name: str, record_id: str) -> dict:
    """Delete a Salesforce record by Id with retry."""

    def _do(sf):
        return getattr(sf, object_name).delete(record_id)

    return _with_retry(_do)


def upsert_record(
    object_name: str, external_id_field: str, external_id: str, data: dict
) -> dict:
    """Upsert a Salesforce record using an external ID field with retry."""

    def _do(sf):
        return getattr(sf, object_name).upsert(
            f"{external_id_field}/{external_id}", data
        )

    return _with_retry(_do)
