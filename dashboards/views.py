# dashboards/views.py
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .selectors import DashboardFilters, DashboardSelectors
from .serializers import DashboardPrincipalSerializer  # <-- Importe o serializer


class DashboardPrincipalAPIView(APIView):
    """
    API principal do dashboard.
    Retorna KPIs e dados de gráficos com base nos filtros fornecidos.
    """

    serializer_class = DashboardPrincipalSerializer  # <-- Adicione isso

    @extend_schema(
        summary="Dados do Dashboard Principal",
        description="Retorna KPIs e dados de gráficos agregados.",
        responses={200: DashboardPrincipalSerializer},
    )
    def get(self, request):
        filters = self._parse_filters(request.query_params)
        selectors = DashboardSelectors(filters=filters)

        data = {
            "kpis": self._build_kpis(selectors),
            "charts": self._build_charts(selectors),
        }

        # Opcional: valide os dados com o serializer (não é obrigatório)
        # serializer = DashboardPrincipalSerializer(data=data)
        # serializer.is_valid(raise_exception=True)

        return Response(data, status=status.HTTP_200_OK)

    def _parse_filters(self, query_params) -> DashboardFilters:
        """Converte query params em objeto DashboardFilters."""
        start_date = self._parse_date(query_params.get("start_date"))
        end_date = self._parse_date(query_params.get("end_date"))
        return DashboardFilters(start_date=start_date, end_date=end_date)

    def _parse_date(self, date_str: str):
        """Converte string 'YYYY-MM-DD' em objeto date."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _build_kpis(self, selectors: DashboardSelectors) -> dict:
        """Monta dicionário com todos os KPIs."""
        return {
            "vendas": str(selectors.get_kpi_vendas()),
            "ticket_medio": str(selectors.get_kpi_ticket_medio()),
            "clientes": selectors.get_kpi_clientes(),
            "pedidos": selectors.get_kpi_pedidos(),
            "a_receber": str(selectors.get_kpi_a_receber()),
            "estoque_baixo": selectors.get_kpi_estoque_baixo(),
        }

    def _build_charts(self, selectors: DashboardSelectors) -> dict:
        """Monta dicionário com todos os dados de gráficos."""
        return {
            "evolucao_vendas": selectors.get_evolucao_vendas(),
            "top_produtos": selectors.get_top_produtos(limit=5),
            "meios_pagamento": selectors.get_meios_pagamento(),
            "pedidos_por_status": selectors.get_pedidos_por_status(),
        }
