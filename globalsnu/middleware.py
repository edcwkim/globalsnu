from django.middleware import locale


class LocaleMiddleware(locale.LocaleMiddleware):
    """
    A customized locale middleware that does not search for HTTP_ACCEPT_LANGUAGE
    values in `request.META`.
    """

    def process_request(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            request.META['HTTP_ACCEPT_LANGUAGE'] = "*"
        super().process_request(request)
