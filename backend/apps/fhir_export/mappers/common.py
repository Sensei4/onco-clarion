"""Common constants and helpers for FHIR mappers."""

from datetime import date, datetime
from typing import Any

# ---------------------------------------------------------------------------
# Identifier systems (our own URN namespace)
# ---------------------------------------------------------------------------
SYSTEM_MRN = "urn:onco-clarion:mrn"
SYSTEM_USERNAME = "urn:onco-clarion:username"
SYSTEM_ICD11_MMS = "http://id.who.int/icd/release/11/2026-01/mms"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def format_date(value: date | None) -> str | None:
    """Format a date for FHIR (YYYY-MM-DD)."""
    if value is None:
        return None
    return value.isoformat()


def format_datetime(value: datetime | None) -> str | None:
    """Format a datetime for FHIR (ISO 8601 with timezone)."""
    if value is None:
        return None
    return value.isoformat()


def split_full_name(full_name: str) -> dict[str, list[str]]:
    """Split a full name into family / given parts.

    Assumes the last word is the family name and everything before is given.
    This is a pragmatic heuristic; real name parsing is locale-specific.
    """
    parts = full_name.strip().split()
    if not parts:
        return {"family": "", "given": []}
    if len(parts) == 1:
        return {"family": parts[0], "given": []}
    return {
        "family": parts[-1],
        "given": parts[:-1],
    }


def safe_str(value: Any) -> str:
    """Return a string representation, or empty string for None."""
    if value is None:
        return ""
    return str(value)
