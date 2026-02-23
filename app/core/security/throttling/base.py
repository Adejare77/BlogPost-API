from rest_framework.throttling import SimpleRateThrottle


class BaseUserOrIPThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = f"user_{request.user.id}"
        else:
            ident = self.get_ident(request=request)

        return self.cache_format % {"scope": self.scope, "ident": ident}
