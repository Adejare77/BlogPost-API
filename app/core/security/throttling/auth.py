from app.core.security.throttling.base import BaseUserOrIPThrottle

class LoginThrottle(BaseUserOrIPThrottle):
    scope = "auth_login"

class RegisterThrottle(BaseUserOrIPThrottle):
    scope = "auth_register"

class PasswordResetThrottle(BaseUserOrIPThrottle):
    scope = "auth_password_reset"
