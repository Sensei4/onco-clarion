from django.middleware.csrf import get_token


class EnsureCsrfCookieMiddleware:
    """Ensure the CSRF cookie is set on every response.

    Required for SPA clients that read the csrftoken cookie
    and send it back in the X-CSRFToken header on unsafe requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        get_token(request)
        return self.get_response(request)
