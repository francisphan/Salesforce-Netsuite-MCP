"""Input sanitization utilities for SOQL, SuiteQL, and SOSL query interpolation,
plus validators for API name and path-segment parameters."""

import re


def escape_soql(value: str) -> str:
    """Escape a string value for safe interpolation into a SOQL ``WHERE field = '...'`` clause.

    SOQL uses backslash-escaping for special characters inside single-quoted strings.
    See: https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta

    NOTE: This does NOT escape ``%`` and ``_`` wildcards used in ``LIKE`` clauses.
    If you need LIKE-safe escaping, call :func:`escape_soql_like` instead.
    """
    value = value.replace("\\", "\\\\")
    value = value.replace("'", "\\'")
    value = value.replace('"', '\\"')
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\t", "\\t")
    value = value.replace("\b", "\\b")
    value = value.replace("\f", "\\f")
    value = value.replace("\0", "")
    return value


def escape_soql_like(value: str) -> str:
    """Escape a string value for safe interpolation into a SOQL ``LIKE`` clause.

    Escapes everything :func:`escape_soql` does, plus the ``%`` and ``_`` wildcards.
    """
    value = escape_soql(value)
    value = value.replace("%", "\\%")
    value = value.replace("_", "\\_")
    return value


def escape_suiteql(value: str) -> str:
    """Escape a string value for safe interpolation into a SuiteQL query.

    SuiteQL follows standard SQL escaping: single quotes are doubled.
    Backslashes are also doubled to prevent escape-sequence tricks, and null
    bytes are stripped.
    """
    value = value.replace("\\", "\\\\")
    value = value.replace("'", "''")
    value = value.replace("\0", "")
    return value


# ---------------------------------------------------------------------------
# SOSL escaping
# ---------------------------------------------------------------------------

# Characters reserved by Salesforce SOSL that must be backslash-escaped inside
# the FIND {…} clause.  Reference:
# https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_sosl_find.htm
_SOSL_RESERVED = set('?&|!{}[]()^~*:\\\'-+"')


def escape_sosl(value: str) -> str:
    """Escape a string value for safe interpolation into a SOSL ``FIND {…}`` clause.

    All SOSL reserved characters are backslash-escaped.
    """
    out: list[str] = []
    for ch in value:
        if ch in _SOSL_RESERVED:
            out.append("\\")
        out.append(ch)
    return "".join(out)


# ---------------------------------------------------------------------------
# Identifier / path-segment validators
# ---------------------------------------------------------------------------

_SF_ID_PATTERN = re.compile(r"^[a-zA-Z0-9]{15}([a-zA-Z0-9]{3})?$")


def validate_sf_id(value: str) -> str:
    """Validate that a value looks like a Salesforce record ID (exactly 15 or 18 alphanumeric chars).

    Returns the value unchanged if valid, raises ValueError otherwise.
    """
    if not _SF_ID_PATTERN.match(value):
        raise ValueError(f"Invalid Salesforce ID format: {value!r}")
    return value


_OBJECT_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,99}$")


def validate_object_name(value: str) -> str:
    """Validate that a value is a safe SObject / record-type API name.

    Accepts alphanumeric + underscore, starting with a letter or underscore,
    up to 100 characters (covers standard and custom object names like
    ``TVRS_Guest__c``).

    Raises ValueError if the name is invalid.
    """
    if not _OBJECT_NAME_PATTERN.match(value):
        raise ValueError(
            f"Invalid object name: {value!r}. "
            "Must match [a-zA-Z_][a-zA-Z0-9_]{{0,99}}."
        )
    return value


_PATH_SEGMENT_PATTERN = re.compile(r"^[a-zA-Z0-9._@+%-]+$")


def validate_path_segment(value: str) -> str:
    """Validate that a value is safe to use as a single URL path segment.

    Rejects empty strings, path-traversal sequences (``..``, ``/``),
    and characters outside a conservative allowlist.

    Raises ValueError if the value is unsafe.
    """
    if not value or ".." in value or "/" in value:
        raise ValueError(f"Invalid path segment: {value!r}")
    if not _PATH_SEGMENT_PATTERN.match(value):
        raise ValueError(f"Invalid path segment: {value!r}")
    return value
