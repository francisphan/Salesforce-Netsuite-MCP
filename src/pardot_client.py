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


def get_list_membership(membership_id: str, fields: str | None = None) -> dict:
    """GET /list-memberships/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"list-memberships/{membership_id}", params=params)


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


# --- Emails ---

def query_emails(params: dict | None = None) -> dict:
    """GET /emails with optional filter params."""
    return _get("emails", params=params)


def get_email(email_id: str, fields: str | None = None) -> dict:
    """GET /emails/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"emails/{email_id}", params=params)


# --- List Emails ---

def query_list_emails(params: dict | None = None) -> dict:
    """GET /list-emails with optional filter params."""
    return _get("list-emails", params=params)


def get_list_email(list_email_id: str, fields: str | None = None) -> dict:
    """GET /list-emails/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"list-emails/{list_email_id}", params=params)


# --- Custom Fields ---

def query_custom_fields(params: dict | None = None) -> dict:
    """GET /custom-fields with optional filter params."""
    return _get("custom-fields", params=params)


def get_custom_field(field_id: str, fields: str | None = None) -> dict:
    """GET /custom-fields/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"custom-fields/{field_id}", params=params)


# --- Tags ---

def query_tags(params: dict | None = None) -> dict:
    """GET /tags with optional filter params."""
    return _get("tags", params=params)


def get_tag(tag_id: str, fields: str | None = None) -> dict:
    """GET /tags/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"tags/{tag_id}", params=params)


# --- Tagged Objects ---

def query_tagged_objects(params: dict | None = None) -> dict:
    """GET /tagged-objects with optional filter params."""
    return _get("tagged-objects", params=params)


def get_tagged_object(tagged_object_id: str, fields: str | None = None) -> dict:
    """GET /tagged-objects/{id}."""
    params = {"fields": fields} if fields else None
    return _get(f"tagged-objects/{tagged_object_id}", params=params)


# --- Tracker Domains ---

def query_tracker_domains(params: dict | None = None) -> dict:
    """GET /tracker-domains with optional filter params."""
    return _get("tracker-domains", params=params)


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
        if not resp.ok:
            raise Exception(f"{resp.status_code} {resp.reason}: {resp.text}")
        return resp.json()
    return _with_retry(_do)


def _patch(endpoint: str, body: dict) -> dict:
    """PATCH helper that returns parsed JSON with retry."""
    def _do(session):
        resp = session.patch(f"{BASE_URL}/{endpoint}", json=body)
        if not resp.ok:
            raise Exception(f"{resp.status_code} {resp.reason}: {resp.text}")
        if resp.status_code == 204 or not resp.content or not resp.text.strip():
            return {"success": True}
        return resp.json()
    return _with_retry(_do)


def _delete(endpoint: str) -> dict:
    """DELETE helper that returns parsed JSON (or success flag on 204) with retry."""
    def _do(session):
        resp = session.delete(f"{BASE_URL}/{endpoint}")
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content or not resp.text.strip():
            return {"success": True}
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


def delete_prospect(prospect_id: str) -> dict:
    """Delete a Pardot prospect by ID.

    Args:
        prospect_id: The Pardot prospect ID.

    Returns:
        A success dict, or raises on failure.
    """
    return _delete(f"prospects/{prospect_id}")


def upsert_prospect_by_email(data: dict) -> dict:
    """Upsert a prospect by email — creates or updates the most recent match.

    Args:
        data: Dict of prospect fields; must include 'email'.

    Returns:
        The created or updated prospect as a dict.
    """
    return _post("prospects/do/upsertLatestByEmail", data)


def undelete_prospect(prospect_id: str) -> dict:
    """Restore a previously deleted Pardot prospect.

    Args:
        prospect_id: The Pardot prospect ID to restore.

    Returns:
        The restored prospect as a dict.
    """
    return _post(f"prospects/{prospect_id}/do/undelete", {})


# --- List Write Operations ---

def create_list(data: dict) -> dict:
    """Create a new Pardot list.

    Args:
        data: Dict of list fields (e.g. name, title, description).

    Returns:
        The created list as a dict.
    """
    return _post("lists", data)


def update_list(list_id: str, data: dict) -> dict:
    """Update an existing Pardot list.

    Args:
        list_id: The Pardot list ID.
        data: Dict of fields to update.

    Returns:
        The updated list as a dict.
    """
    return _patch(f"lists/{list_id}", data)


def delete_list(list_id: str) -> dict:
    """Delete a Pardot list by ID.

    Args:
        list_id: The Pardot list ID.

    Returns:
        A success dict, or raises on failure.
    """
    return _delete(f"lists/{list_id}")


# --- List Membership Write Operations ---

def create_list_membership(data: dict) -> dict:
    """Create a new list membership.

    Args:
        data: Dict with listId and prospectId.

    Returns:
        The created membership as a dict.
    """
    return _post("list-memberships", data)


def update_list_membership(membership_id: str, data: dict) -> dict:
    """Update an existing list membership.

    Args:
        membership_id: The list membership ID.
        data: Dict of fields to update.

    Returns:
        The updated membership as a dict.
    """
    return _patch(f"list-memberships/{membership_id}", data)


def delete_list_membership(membership_id: str) -> dict:
    """Delete a list membership by ID.

    Args:
        membership_id: The list membership ID.

    Returns:
        A success dict, or raises on failure.
    """
    return _delete(f"list-memberships/{membership_id}")


# --- Email Write Operations ---

def create_email(data: dict) -> dict:
    """Send a one-to-one Pardot email.

    Args:
        data: Dict with prospectId, emailTemplateId, campaignId, etc.

    Returns:
        The created email as a dict.
    """
    return _post("emails", data)


def create_list_email(data: dict) -> dict:
    """Send a Pardot email to a list.

    Args:
        data: Dict with name, listId, emailTemplateId, campaignId, etc.

    Returns:
        The created list email as a dict.
    """
    return _post("list-emails", data)


# --- Email Template Write Operations ---

def update_email_template(template_id: str, data: dict) -> dict:
    """Update an existing Pardot email template.

    Args:
        template_id: The email template ID.
        data: Dict of fields to update.

    Returns:
        The updated email template as a dict.
    """
    return _patch(f"email-templates/{template_id}", data)


def delete_email_template(template_id: str) -> dict:
    """Delete a Pardot email template by ID.

    Args:
        template_id: The email template ID.

    Returns:
        A success dict, or raises on failure.
    """
    return _delete(f"email-templates/{template_id}")


# --- Custom Field Write Operations ---

def create_custom_field(data: dict) -> dict:
    """Create a new Pardot custom field.

    Args:
        data: Dict of custom field properties (e.g. name, fieldId, type).

    Returns:
        The created custom field as a dict.
    """
    return _post("custom-fields", data)


def update_custom_field(field_id: str, data: dict) -> dict:
    """Update an existing Pardot custom field.

    Args:
        field_id: The custom field ID.
        data: Dict of fields to update.

    Returns:
        The updated custom field as a dict.
    """
    return _patch(f"custom-fields/{field_id}", data)


def delete_custom_field(field_id: str) -> dict:
    """Delete a Pardot custom field by ID.

    Args:
        field_id: The custom field ID.

    Returns:
        A success dict, or raises on failure.
    """
    return _delete(f"custom-fields/{field_id}")


# --- Tag Write Operations ---

def create_tag(data: dict) -> dict:
    """Create a new Pardot tag.

    Args:
        data: Dict with tag properties (e.g. name).

    Returns:
        The created tag as a dict.
    """
    return _post("tags", data)


def update_tag(tag_id: str, data: dict) -> dict:
    """Update an existing Pardot tag.

    Args:
        tag_id: The tag ID.
        data: Dict of fields to update.

    Returns:
        The updated tag as a dict.
    """
    return _patch(f"tags/{tag_id}", data)


def delete_tag(tag_id: str) -> dict:
    """Delete a Pardot tag by ID.

    Args:
        tag_id: The tag ID.

    Returns:
        A success dict, or raises on failure.
    """
    return _delete(f"tags/{tag_id}")
