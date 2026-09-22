"""Helpers for writing audit events."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from .models import AuditEvent


def get_client_ip(request: HttpRequest) -> str | None:
    """Extract client IP from request, respecting X-Forwarded-For."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        # X-Forwarded-For can contain a comma-separated list; take the first
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_audit(
    request: HttpRequest,
    action: str,
    entity: Any | None = None,
    *,
    entity_type: str | None = None,
    entity_id: int | None = None,
    entity_repr: str = "",
) -> AuditEvent:
    """Write an AuditEvent.

    Can be called with either:
      - an `entity` object (uses its class name and pk)
      - explicit `entity_type` / `entity_id` / `entity_repr` (for edge cases)
    """
    if entity is not None:
        entity_type = entity.__class__.__name__
        entity_id = getattr(entity, "pk", None)
        try:
            entity_repr = str(entity)[:255]
        except Exception:  # noqa: BLE001
            entity_repr = ""

    user = (
        request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    )

    # Try to resolve the user's organization
    organization = None
    if user is not None:
        organization = getattr(user, "organization", None)

    return AuditEvent.objects.create(
        user=user,
        action=action,
        entity_type=entity_type or "Unknown",
        entity_id=entity_id,
        entity_repr=(entity_repr or "")[:255],
        organization=organization,
        ip_address=get_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:255],
        request_method=request.method,
        request_path=request.path[:512],
    )
