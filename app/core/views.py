from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class HealthCheck(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            connection.cursor()
            return Response({"status": "OK"}, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(
                {
                    "status": "error",
                    "detail": str(err)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
