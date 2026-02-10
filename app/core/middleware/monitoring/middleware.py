import time

from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "api_request_total",
    "Total number of API requests",
    ["method", "endpoint", "http_status"],
)

REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "API request latency in seconds",
    ["method", "endpoint"],
)

IN_PROGRESS = Gauge(
    "api_request_in_progress", "Requests currently in progress", ["method", "endpoint"]
)


class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        IN_PROGRESS.labels(request.method, request.path).inc()

        response = self.get_response(request)
        duration = time.perf_counter() - start
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, request.path).observe(duration)
        IN_PROGRESS.labels(request.method, request.path).dec()

        return response
