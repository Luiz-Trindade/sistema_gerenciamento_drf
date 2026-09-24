# dashboards/urls.py

from django.urls import path
from .views import DashboardPrincipalAPIView, EstoqueResumoAPIView

app_name = "dashboards"

urlpatterns = [
    path("principal/", DashboardPrincipalAPIView.as_view(), name="dashboard-principal"),
    path("estoque/", EstoqueResumoAPIView.as_view(), name="estoque-resumo"),
]
