# dashboards/views.py
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .selectors import (
    DashboardFilters,
    DashboardSelectors,
    EstoqueFilters,
    EstoqueSelectors,
    VendasFilters,
    VendasSelectors,
)
from .serializers import DashboardPrincipalSerializer


def _parse_date(date_str: str):
    """Converte 'YYYY-MM-DD' em date, ou None se inválido/ausente."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


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


class EstoqueResumoAPIView(APIView):
    """
    Resumo do módulo Estoque.

    Alimenta a página de entrada do estoque com KPIs de topo,
    listas de alertas acionáveis e feed de movimentações recentes.
    """

    serializer_class = None  # opcional: criar EstoqueResumoSerializer

    @extend_schema(
        summary="Resumo do módulo Estoque",
        description=(
            "Retorna KPIs, alertas (abaixo do mínimo, zerados, sem "
            "movimentação) e as últimas movimentações registradas."
        ),
        responses={200: dict},
    )
    def get(self, request):
        filters = EstoqueFilters(
            start_date=_parse_date(request.query_params.get("start_date")),
            end_date=_parse_date(request.query_params.get("end_date")),
            limite_baixo=int(request.query_params.get("limite_baixo", 5)),
            dias_parado=int(request.query_params.get("dias_parado", 90)),
        )
        selectors = EstoqueSelectors(filters=filters)

        data = {
            "kpis": {
                "total_produtos": selectors.get_kpi_total_produtos(),
                "valor_estoque": str(selectors.get_kpi_valor_estoque()),
                "abaixo_minimo": selectors.get_kpi_abaixo_minimo(),
                "zerados": selectors.get_kpi_zerados(),
                "movimentacoes": selectors.get_kpi_movimentacoes(),
                "entradas": selectors.get_kpi_entradas(),
                "saidas": selectors.get_kpi_saidas(),
            },
            "alertas": {
                "abaixo_minimo": selectors.get_alertas_abaixo_minimo(limit=5),
                "zerados": selectors.get_alertas_zerados(limit=5),
                "sem_movimentacao": selectors.get_alertas_sem_movimentacao(limit=5),
            },
            "atividades_recentes": selectors.get_movimentacoes_recentes(limit=10),
        }
        return Response(data, status=status.HTTP_200_OK)


class VendasResumoAPIView(APIView):
    """
    Resumo do módulo Vendas.

    Alimenta a página de entrada de vendas com KPIs de topo,
    listas de alertas acionáveis (contas vencidas, contas a
    vencer, pedidos parados) e feed de atividades recentes.
    """

    serializer_class = None  # opcional: criar VendasResumoSerializer

    @extend_schema(
        summary="Resumo do módulo Vendas",
        description=(
            "Retorna KPIs, alertas (contas vencidas, contas a vencer, "
            "pedidos parados) e as últimas atividades registradas."
        ),
        responses={200: dict},
    )
    def get(self, request):
        filters = VendasFilters(
            start_date=_parse_date(request.query_params.get("start_date")),
            end_date=_parse_date(request.query_params.get("end_date")),
            dias_vencimento_proximo=int(
                request.query_params.get("dias_vencimento_proximo", 7)
            ),
            dias_pedido_parado=int(request.query_params.get("dias_pedido_parado", 7)),
        )
        selectors = VendasSelectors(filters=filters)

        data = {
            "kpis": {
                "vendas": str(selectors.get_kpi_vendas()),
                "ticket_medio": str(selectors.get_kpi_ticket_medio()),
                "pedidos": selectors.get_kpi_pedidos(),
                "clientes": selectors.get_kpi_clientes(),
                "cancelados": selectors.get_kpi_cancelados(),
                "a_receber": str(selectors.get_kpi_a_receber()),
                "recebido": str(selectors.get_kpi_recebido()),
            },
            "alertas": {
                "contas_vencidas": selectors.get_alertas_contas_vencidas(limit=5),
                "contas_a_vencer": selectors.get_alertas_contas_a_vencer(limit=5),
                "pedidos_parados": selectors.get_alertas_pedidos_parados(limit=5),
            },
            "pedidos_recentes": selectors.get_pedidos_recentes(limit=10),
            "pagamentos_recentes": selectors.get_pagamentos_recentes(limit=10),
        }
        return Response(data, status=status.HTTP_200_OK)
