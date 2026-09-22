"""Mixin to automatically log audit events from DRF ViewSets."""

from __future__ import annotations

from typing import Any

from .models import AuditEvent
from .utils import log_audit


class AuditLogMixin:
    """Log `view`, `create`, `update`, `delete` actions on DRF ViewSets.

    The mixin hooks into `retrieve`, `create`, `update`, `partial_update`,
    and `destroy`. Subclasses should set:

        audit_entity_type: str       # e.g. "Patient"

    The mixin is intentionally simple: it logs only operations
    that target a single object. List operations are not logged.
    """

    audit_entity_type: str = "Unknown"

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        try:
            obj = self.get_object()
            log_audit(request, AuditEvent.Action.VIEW, entity=obj)
        except Exception:  # noqa: BLE001
            pass
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        try:
            log_audit(
                request,
                AuditEvent.Action.CREATE,
                entity_type=self.audit_entity_type,
                entity_id=response.data.get("id"),
                entity_repr=str(response.data.get("id")),
            )
        except Exception:  # noqa: BLE001
            pass
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        try:
            obj = self.get_object()
            log_audit(request, AuditEvent.Action.UPDATE, entity=obj)
        except Exception:  # noqa: BLE001
            pass
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        try:
            obj = self.get_object()
            log_audit(request, AuditEvent.Action.UPDATE, entity=obj)
        except Exception:  # noqa: BLE001
            pass
        return response

    def destroy(self, request, *args, **kwargs):
        # Get the object BEFORE deletion
        try:
            obj = self.get_object()
            entity_type = obj.__class__.__name__
            entity_id = obj.pk
            try:
                entity_repr = str(obj)[:255]
            except Exception:  # noqa: BLE001
                entity_repr = ""
        except Exception:  # noqa: BLE001
            entity_type, entity_id, entity_repr = self.audit_entity_type, None, ""

        response = super().destroy(request, *args, **kwargs)

        try:
            log_audit(
                request,
                AuditEvent.Action.DELETE,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_repr=entity_repr,
            )
        except Exception:  # noqa: BLE001
            pass
        return response


def log_custom_action(request, entity: Any, action: str) -> None:
    """Helper for custom actions (e.g. download, complete, cancel)."""
    log_audit(request, action, entity=entity)
