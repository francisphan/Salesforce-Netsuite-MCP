"""Pardot (Account Engagement) API v5 client, reusing Salesforce OAuth token."""

import os
import time

import requests
from dotenv import load_dotenv

from src.sf_client import get_client as get_sf_client, _reconnect as sf_reconnect, _sf_holder

load_dotenv()

BASE_URL = "https://pi.pardot.com/api/v5/objects"

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubled each retry

_pardot_session: list[requests.Session | None] = [None]


def _get_business_unit_id() -> str:
    buid = os.environ.get("PARDOT_BUSINESS_UNIT_ID")
    if not buid:
        raise RuntimeError("PARDOT_BUSINESS_UNIT_ID environment variable is required.")
    return buid


def _get_access_token() -> str:
    """Get the current Salesforce access token for Pardot API auth."""
    sf = get_sf_client()
    return sf.session_id


def _build_session() -> requests.Session:
    """Create a requests.Session pre-configured with Pardot auth headers."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {_get_access_token()}",
        "Pardot-Business-Unit-Id": _get_business_unit_id(),
        "Content-Type": "application/json",
    })
    return session


def get_session() -> requests.Session:
    """Return a configured Pardot session (singleton — rebuilds if needed)."""
    if _pardot_session[0] is None:
        _pardot_session[0] = _build_session()
    return _pardot_session[0]


def _refresh_session():
    """Re-authenticate Salesforce and rebuild the Pardot session."""
    _sf_holder[0] = sf_reconnect()
    _pardot_session[0] = _build_session()


def _with_retry(func):
    """Execute func(session) with retry on transient errors and re-auth on 401."""
    session = get_session()
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            return func(session)
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                status = e.response.status_code
                if status == 401:
                    _refresh_session()
                    session = get_session()
                    continue
                # Don't retry client errors (4xx) — they won't succeed on retry
                if 400 <= status < 500:
                    raise
            last_exc = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2**attempt))
            continue
        except Exception as e:
            last_exc = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2**attempt))
            continue
    raise last_exc


def _get(endpoint: str, params: dict | None = None) -> dict | list:
    """GET helper that returns parsed JSON with retry."""
    def _do(session):
        resp = session.get(f"{BASE_URL}/{endpoint}", params=params)
        resp.raise_for_status()
        return resp.json()
    return _with_retry(_do)


# --- Prospects ---

def query_prospects(params: dict | None = None) -> dict:
    """GET /prospects with optional filter params."""
    return _get("prospects", params=params)


def get_prospect(prospect_id: str, fields: str | None = None) -> dict:
    """GET /prospects/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"prospects/{prospect_id}", params=params)


# --- Lists ---

def query_lists(params: dict | None = None) -> dict:
    """GET /lists with optional filter params."""
    return _get("lists", params=params)


def get_list(list_id: str, fields: str | None = None) -> dict:
    """GET /lists/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"lists/{list_id}", params=params)


# --- List Memberships ---

def query_list_memberships(params: dict | None = None) -> dict:
    """GET /list-memberships with optional filter params."""
    return _get("list-memberships", params=params)


# --- Campaigns ---

def query_campaigns(params: dict | None = None) -> dict:
    """GET /campaigns with optional filter params (read-only)."""
    return _get("campaigns", params=params)


def get_campaign(campaign_id: str, fields: str | None = None) -> dict:
    """GET /campaigns/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"campaigns/{campaign_id}", params=params)


# --- Visitor Activities ---

def query_visitor_activities(params: dict | None = None) -> dict:
    """GET /visitor-activities with optional filter params."""
    return _get("visitor-activities", params=params)


# --- Forms ---

def query_forms(params: dict | None = None) -> dict:
    """GET /forms with optional filter params."""
    return _get("forms", params=params)


def get_form(form_id: str, fields: str | None = None) -> dict:
    """GET /forms/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"forms/{form_id}", params=params)


# --- Email Templates ---

def query_email_templates(params: dict | None = None) -> dict:
    """GET /email-templates with optional filter params."""
    return _get("email-templates", params=params)


def get_email_template(template_id: str, fields: str | None = None) -> dict:
    """GET /email-templates/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"email-templates/{template_id}", params=params)


# --- Write Helpers ---

def _post(endpoint: str, body: dict) -> dict:
    """POST helper that returns parsed JSON with retry."""
    def _do(session):
        resp = session.post(f"{BASE_URL}/{endpoint}", json=body)
        resp.raise_for_status()
        return resp.json()
    return _with_retry(_do)


def _patch(endpoint: str, body: dict) -> dict:
    """PATCH helper that returns parsed JSON with retry."""
    def _do(session):
        resp = session.patch(f"{BASE_URL}/{endpoint}", json=body)
        resp.raise_for_status()
        return resp.json()
    return _with_retry(_do)


# --- Prospect Write Operations ---

def create_prospect(data: dict) -> dict:
    """Create a new Pardot prospect.

    Args:
        data: Dict of prospect fields (e.g. email, firstName, lastName).

    Returns:
        The created prospect as a dict.
    """
    return _post("prospects", data)


def create_email_template(data: dict) -> dict:
    """Create a new Pardot email template.

    Args:
        data: Dict of email template fields (e.g. name, subject, htmlMessage, folderId).

    Returns:
        The created email template as a dict.
    """
    return _post("email-templates", data)


def update_prospect(prospect_id: str, data: dict) -> dict:
    """Update an existing Pardot prospect.

    Args:
        prospect_id: The Pardot prospect ID.
        data: Dict of fields to update.

    Returns:
        The updated prospect as a dict.
    """
    return _patch(f"prospects/{prospect_id}", data)
