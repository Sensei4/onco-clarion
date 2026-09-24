"""HTTP client for the local ICD-API Docker container.

The container runs at http://icd-api:80 (see docker-compose.yml).
All requests require the header `API-Version: v2`.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

import requests
from django.conf import settings

from .exceptions import (
    IcdApiNotFoundError,
    IcdApiTimeoutError,
    IcdApiUnavailableError,
)

logger = logging.getLogger(__name__)


DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2

_HIGHLIGHT_RE = re.compile(r"</?em[^>]*>")


def _strip_highlight(text: str) -> str:
    """Remove <em class='found'>...</em> tags from ICD-API search labels."""
    return _HIGHLIGHT_RE.sub("", text).strip()


class IcdApiClient:
    """HTTP client for the ICD-API v2.

    Usage:
        client = IcdApiClient()
        entity = client.get_foundation_entity("1047754165")
    """

    def __init__(
        self,
        base_url: str | None = None,
        language: str = "en",
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        self.base_url = (base_url or settings.ICD_API_URL).rstrip("/")
        self.language = language
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "API-Version": "v2",
                "Accept": "application/json",
                "Accept-Language": language,
            }
        )

    # ------------------------------------------------------------------
    # Low-level HTTP
    # ------------------------------------------------------------------
    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Perform a GET request with retry on transient errors."""
        url = f"{self.base_url}{path}"
        last_error: Exception | None = None

        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )
            except requests.Timeout as exc:
                last_error = exc
                logger.warning(
                    "ICD-API timeout on %s (attempt %d/%d)",
                    url,
                    attempt,
                    self.retries,
                )
                if attempt < self.retries:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                    continue
                raise IcdApiTimeoutError(f"Timeout on {url}") from exc
            except requests.ConnectionError as exc:
                last_error = exc
                logger.warning(
                    "ICD-API connection error on %s (attempt %d/%d)",
                    url,
                    attempt,
                    self.retries,
                )
                if attempt < self.retries:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                    continue
                raise IcdApiUnavailableError(f"Connection error on {url}") from exc

            if response.status_code == 404:
                raise IcdApiNotFoundError(f"Not found: {url}")

            if response.status_code >= 500:
                last_error = IcdApiUnavailableError(f"{response.status_code} on {url}")
                logger.warning(
                    "ICD-API server error %d on %s (attempt %d/%d)",
                    response.status_code,
                    url,
                    attempt,
                    self.retries,
                )
                if attempt < self.retries:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                    continue
                raise last_error

            if response.status_code >= 400:
                raise IcdApiUnavailableError(
                    f"Client error {response.status_code} on {url}: {response.text[:200]}"
                )

            try:
                return response.json()
            except ValueError as exc:
                raise IcdApiUnavailableError(f"Invalid JSON from {url}") from exc

        # Should not reach here, but for mypy
        raise IcdApiUnavailableError(f"Failed after {self.retries} attempts: {last_error}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_foundation_entity(self, entity_id: str | int) -> dict[str, Any]:
        """Fetch a foundation entity by its numeric id.

        Example: get_foundation_entity("1047754165") returns the entity
        for "Malignant neoplasms of breast".
        """
        return self._get(f"/icd/entity/{entity_id}")

    def get_mms_root(self, release_id: str = "2026-01") -> dict[str, Any]:
        """Fetch the MMS root entity (list of all chapters)."""
        return self._get(f"/icd/release/11/{release_id}/mms")

    def get_mms_entity(self, mms_uri: str) -> dict[str, Any]:
        """Fetch an MMS entity by its full URI.

        The `mms_uri` is the path after `/icd/release/11/{release}/mms`,
        e.g. "1435254666" or "1047754165/unspecified".
        """
        release_id = "2026-01"
        # Extract the trailing part if a full URI was provided
        marker = "/mms/"
        if marker in mms_uri:
            mms_uri = mms_uri.split(marker, 1)[1]
        return self._get(f"/icd/release/11/{release_id}/mms/{mms_uri}")

    def search_mms(
        self,
        query: str,
        release_id: str = "2026-01",
        flat: bool = True,
    ) -> dict[str, Any]:
        """Search the MMS linearization.

        Returns a dict with `destinationEntities` — the list of matches.
        Each match has `theCode`, `title`, `id` (URI). Highlight tags
        in titles are stripped.
        """
        params: dict[str, Any] = {"q": query}
        if flat:
            params["flat"] = "true"
        data = self._get(
            f"/icd/release/11/{release_id}/mms/search",
            params=params,
        )
        # Clean <em class='found'>...</em> tags in titles
        for entity in data.get("destinationEntities", []):
            if "title" in entity and isinstance(entity["title"], str):
                entity["title"] = _strip_highlight(entity["title"])
        return data

    # ------------------------------------------------------------------
    # Helpers for extracting structured data from raw API responses
    # ------------------------------------------------------------------
    @staticmethod
    def extract_code(entity: dict[str, Any]) -> str:
        """Extract the code from an MMS entity.

        Chapters use `code` (e.g. "01"), other entities use `theCode`
        (e.g. "2C6Z"). Returns an empty string if neither is present.
        """
        return entity.get("theCode") or entity.get("code") or ""

    @staticmethod
    def extract_synonyms(entity: dict[str, Any]) -> list[str]:
        """Extract synonym strings from an MMS or foundation entity.

        Works with:
          - MMS search results (matchingPVs with propertyId='Synonym')
          - Foundation entities (synonym list with label.@value)
        """
        result: list[str] = []
        seen: set[str] = set()

        # MMS search results: matchingPVs
        for pv in entity.get("matchingPVs", []) or []:
            if pv.get("propertyId") == "Synonym":
                label = _strip_highlight(pv.get("label", ""))
                if label and label not in seen:
                    seen.add(label)
                    result.append(label)

        # Foundation entities: synonym field
        for syn in entity.get("synonym", []) or []:
            label = ""
            if isinstance(syn, dict):
                label_value = syn.get("label", {})
                if isinstance(label_value, dict):
                    label = label_value.get("@value", "")
                elif isinstance(label_value, str):
                    label = label_value
            elif isinstance(syn, str):
                label = syn
            label = _strip_highlight(label)
            if label and label not in seen:
                seen.add(label)
                result.append(label)

        return result

    @staticmethod
    def extract_title(entity: dict[str, Any]) -> str:
        """Extract the title from a foundation or MMS entity.

        Foundation entities use {"@value": "...", "@language": "en"}.
        MMS entities return a plain string.
        """
        title = entity.get("title", "")
        if isinstance(title, dict):
            return title.get("@value", "")
        if isinstance(title, str):
            return _strip_highlight(title)
        return ""
