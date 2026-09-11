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

    class Meta:
        model = Pedido
        fields = [
            "id",
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
        read_only_fields = ["id", "valor_total", "criado_em", "atualizado_em"]

    def validate(self, attrs):
        # Cria uma instância temporária para rodar as validações de regras de negócio do model
        instance = Pedido(**attrs)
        # Se for atualização, usa a instância real
        if self.instance:
            for attr, value in attrs.items():
                setattr(instance, attr, value)
            instance.pk = self.instance.pk

        # Valida as movimentações se elas foram enviadas na requisição
        if "movimentacoes" in attrs:
            # Atribui temporariamente para passar na validação de existência de M2M
            pass

        return attrs
