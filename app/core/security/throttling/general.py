from app.core.security.throttling.base import BaseUserOrIPThrottle


class UserThrottling(BaseUserOrIPThrottle):
    scope = "user"


class AnonThrottling(BaseUserOrIPThrottle):
    scope = "anon"
