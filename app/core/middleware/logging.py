import logging
import time
import uuid
import random
from django.conf import settings

logger = logging.getLogger("request_logger")


class RequestResponseLoggingMiddleware:
    SKIP_PATHS = ['/metrics/', '/health/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in self.SKIP_PATHS:
            return self.get_response(request)

        request_id = request.headers.get('X-request-ID') or str(uuid.uuid4())
        request.request_id = request_id

        start = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception:
            logger.exception(
                "Request failed",
                extra=self._log_content(request, None, start, request_id)
            )
            raise

        log_level = self._get_log_level(request, response)
        if log_level:
            logger.log(
                log_level,
                f"{request.method} {request.path} completed with {response.status_code}",
                extra=self._log_content(request, response, start, request_id),
        )

        return response

    def _get_log_level(self, request, response):
        if response.status_code in [401, 403, 404, 429]:
            return logging.WARNING

        if request.method in ['POST', 'PATCH', 'DELETE']:
            return logging.INFO

        # randomly select 10% of get requests
        if settings.LOG_SAMPLING and random.random() > settings.LOG_SAMPLING_RATE:
            return None

        return logging.INFO

    def _log_content(self, request, response, start, request_id):
        duration = (time.perf_counter() - start) * 1000
        return {
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
            "status_code": getattr(response, "status_code", 500),
            "duration_ms": round(duration, 2),
            "user_id": getattr(request.user, "id", None),
            "ip": self._get_client_ip(request),
            "user_agent": request.headers.get('User-Agent', "")[:100]
        }

    def _get_client_ip(self, request):
        x_forwarded = request.headers.get('Forwarded-for')
        return x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR')
