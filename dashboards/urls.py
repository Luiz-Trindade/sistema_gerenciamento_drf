# dashboards/urls.py

from django.urls import path
from .views import DashboardPrincipalAPIView

app_name = "dashboards"

urlpatterns = [
    path("principal/", DashboardPrincipalAPIView.as_view(), name="dashboard-principal"),
]
