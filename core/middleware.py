from django.contrib.sessions.backends.base import UpdateError

class IgnoreSessionUpdateErrorMiddleware:
    """
    Ignore session UpdateError (forced update did not affect any rows)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if hasattr(request, 'session'):
                request.session.save()
        except UpdateError:
            pass
        return response
