from django.urls import path

from app.core.views import HealthCheck

urlpatterns = [path("", HealthCheck.as_view(), name="health-check")]
