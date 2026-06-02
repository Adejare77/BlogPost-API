import logging
import random
import time
import uuid

from django.conf import settings

logger = logging.getLogger("request_logger")


class RequestResponseLoggingMiddleware:
    SKIP_PATHS = ["/metrics/", "/health/"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in self.SKIP_PATHS:
            return self.get_response(request)

        request_id = request.headers.get("X-request-ID") or str(uuid.uuid4())
        request.request_id = request_id

        start = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception:
            logger.exception(
                "Request failed",
                extra=self._log_content(request, None, start),
            )
            raise

        log_level, status = self._get_log_level(request, response)

        if status:
            if status < 400:
                message_success = "completed with"
            elif status < 500:
                message_success = "returned client error"
            else:
                message_success = "failed with server error"

            logger.log(
                log_level,
                f"{request.method} {request.path} {message_success} {response.status_code}",
                extra=self._log_content(request, response, start),
            )

        return response

    def _get_log_level(self, request, response):
        if response.status_code in [400, 401, 403, 404, 429]:
            return logging.WARNING, response.status_code

        if request.method in ["POST", "PATCH", "DELETE"]:
            return logging.INFO, response.status_code

        # logging rate
        if settings.LOG_SAMPLING and random.random() >= settings.LOG_SAMPLING_RATE:
            return None, None

        return logging.INFO, response.status_code

    def _log_content(self, request, response, start):
        duration = (time.perf_counter() - start) * 1000
        return {
            "request_id": request.request_id,
            "method": request.method,
            "path": request.path,
            "status_code": getattr(response, "status_code", 500),
            "duration_ms": round(duration, 2),
            "user_id": getattr(request.user, "id", None),
            "ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", "")[:100],
        }

    def _get_client_ip(self, request):
        x_forwarded = request.headers.get("X-Forwarded-for")
        return (
            x_forwarded.split(",")[0].strip()
            if x_forwarded
            else request.META.get("REMOTE_ADDR")
        )
