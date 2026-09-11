from django.http import JsonResponse


def health(request):
    """Simple healthcheck endpoint. Used by Docker and monitoring."""
    return JsonResponse({"status": "ok", "service": "onco-clarion-backend"})
