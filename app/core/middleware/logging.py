import logging
import time

logger = logging.getLogger("api")


class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start

        logger.info(
            f"{request.method} {request.path} completed with {response.status_code}",
            extra={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ns": round(duration * 1000, 2),
            },
        )

        return response
