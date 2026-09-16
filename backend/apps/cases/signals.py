from django.dispatch import receiver
from django_fsm.signals import post_transition

from .models import CancerCase, StatusTransition


@receiver(post_transition, sender=CancerCase)
def record_status_transition(sender, instance, name, source, target, **kwargs):
    """Create a StatusTransition record after every successful FSM transition.

    `name` is the method name (e.g. 'start_diagnostics').
    `source` is the previous status value.
    `target` is the new status value.
    `_last_transition` was set by the transition method (by_user, reason).
    """
    by_user, reason = getattr(instance, "_last_transition", (None, ""))
    StatusTransition.objects.create(
        case=instance,
        from_status=source,
        to_status=target,
        transitioned_by=by_user,
        reason=reason,
    )
