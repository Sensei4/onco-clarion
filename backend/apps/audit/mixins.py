"""Mixin to automatically log audit events from DRF ViewSets."""

from __future__ import annotations

from typing import Any

from .models import AuditEvent
from .utils import log_audit


def _has_method(obj: Any, name: str) -> bool:
    """Return True if `obj` has a callable attribute `name`."""
    return callable(getattr(obj, name, None))


class AuditLogMixin:
    """Log `view`, `create`, `update`, `delete` actions on DRF ViewSets.

    The mixin hooks into `retrieve`, `create`, `update`, and `destroy`.
    Each hook is a no-op if the parent class does not define the
    corresponding method (e.g. read-only viewsets).
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
        # Skip if parent does not support creation (read-only viewsets)
        parent_create = getattr(super(), "create", None)
        if not callable(parent_create):
            from rest_framework.exceptions import MethodNotAllowed

            raise MethodNotAllowed(request.method)

        response = parent_create(request, *args, **kwargs)
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
        parent_update = getattr(super(), "update", None)
        if not callable(parent_update):
            from rest_framework.exceptions import MethodNotAllowed

            raise MethodNotAllowed(request.method)

        response = parent_update(request, *args, **kwargs)
        try:
            obj = self.get_object()
            log_audit(request, AuditEvent.Action.UPDATE, entity=obj)
        except Exception:  # noqa: BLE001
            pass
        return response

    def partial_update(self, request, *args, **kwargs):
        # partial_update delegates to update in DRF, so we only override update.
        # Call the parent directly to avoid double-logging.
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        parent_destroy = getattr(super(), "destroy", None)
        if not callable(parent_destroy):
            from rest_framework.exceptions import MethodNotAllowed

            raise MethodNotAllowed(request.method)

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

        response = parent_destroy(request, *args, **kwargs)

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
