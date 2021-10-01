from urllib.parse import quote_plus, unquote_plus

from django.shortcuts import redirect, reverse


class STMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != "/login/" and not request.user.is_authenticated:
            next = quote_plus(request.get_full_path())
            response = redirect(reverse("login") + f"?next={next}")
        else:
            response = self.get_response(request)
        return response
