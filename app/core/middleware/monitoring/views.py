from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from rest_framework.views import APIView


class PrivateMetricsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return HttpResponseForbidden("Missing bearer token")

        token = auth_header.split(" ")[1]
        if token != settings.PROMETHEUS_SCRAPE_TOKEN:
            return HttpResponseForbidden("Forbidden")

        return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
