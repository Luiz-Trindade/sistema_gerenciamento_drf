# vendas/serializers.py
from rest_framework import serializers
from .models import ContaReceber, Pedido


class ContaReceberSerializer(serializers.ModelSerializer):
    esta_vencida = serializers.BooleanField(read_only=True)
    valor_restante = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = ContaReceber
        fields = [
            "id",
            "pedido",
            "numero_parcela",
            "total_parcelas",
            "valor",
            "valor_pago",
            "valor_restante",
            "vencimento",
            "meio_pagamento",
            "status",
            "esta_vencida",
            "pago_em",
            "observacao",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "valor_pago", "pago_em", "criado_em", "atualizado_em"]


class PedidoSerializer(serializers.ModelSerializer):
    contas_receber = ContaReceberSerializer(many=True, read_only=True)
    quantidade_total = serializers.IntegerField(read_only=True)
    valor_recebido = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    valor_pendente = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)

    # Tornamos read_only para forçar o uso do endpoint de criação com a lista de 'itens'
    movimentacoes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = [
            "id",
            "cliente",
            "cliente_nome",
            "usuario",
            "movimentacoes",
            "status",
            "valor_total",
            "quantidade_total",
            "valor_recebido",
            "valor_pendente",
            "contas_receber",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = [
            "id",
            "valor_total",
            "quantidade_total",
            "valor_recebido",
            "valor_pendente",
            "criado_em",
            "atualizado_em",
        ]
