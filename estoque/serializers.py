from rest_framework import serializers
from .models import Movimentacao, Produto


class ProdutoSerializer(serializers.ModelSerializer):
    # Alterado de DecimalField para IntegerField para refletir o model
    saldo_estoque = serializers.IntegerField(read_only=True)

    class Meta:
        model = Produto
        fields = [
            "id",
            "nome",
            "descricao",
            "preco",
            "ativo",
            "saldo_estoque",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "saldo_estoque", "criado_em", "atualizado_em"]


class MovimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimentacao
        fields = [
            "id",
            "produto",
            "tipo",
            "quantidade",
            "observacao",
            "criado_em",
        ]
        read_only_fields = ["id", "criado_em"]

    def validate(self, attrs):
        produto = attrs.get("produto")
        tipo = attrs.get("tipo")
        quantidade = attrs.get("quantidade")

        # Validação para impedir saída se o saldo em estoque for insuficiente
        if tipo == Movimentacao.Tipo.SAIDA and produto and quantidade:
            saldo_atual = produto.saldo_estoque
            if quantidade > saldo_atual:
                raise serializers.ValidationError(
                    {
                        "quantidade": (
                            f"Saldo insuficiente em estoque. "
                            f"Saldo atual: {saldo_atual}."
                        )
                    }
                )

        return attrs
