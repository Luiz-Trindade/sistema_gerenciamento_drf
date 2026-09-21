# dashboards/serializers.py
from rest_framework import serializers


class KPISerializer(serializers.Serializer):
    """Serializer para os KPIs do dashboard."""

    vendas = serializers.CharField()
    ticket_medio = serializers.CharField()
    clientes = serializers.IntegerField()
    pedidos = serializers.IntegerField()
    a_receber = serializers.CharField()
    estoque_baixo = serializers.IntegerField()


class ChartDataSerializer(serializers.Serializer):
    """Serializer para dados de gráficos (labels + data)."""

    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField(allow_null=True))


class ChartsSerializer(serializers.Serializer):
    """Serializer para todos os gráficos do dashboard."""

    evolucao_vendas = ChartDataSerializer()
    top_produtos = ChartDataSerializer()
    meios_pagamento = ChartDataSerializer()
    pedidos_por_status = ChartDataSerializer()


class DashboardPrincipalSerializer(serializers.Serializer):
    """Serializer principal do dashboard."""

    kpis = KPISerializer()
    charts = ChartsSerializer()
