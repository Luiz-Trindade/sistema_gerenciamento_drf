from rest_framework import serializers

from .models import Movimentacao, Produto


class ProdutoNestedSerializer(serializers.ModelSerializer):
    """Serializer enxuto para embutir o produto nas respostas."""

    class Meta:
        model = Produto
        fields = ["id", "nome"]


class ProdutoRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Aceita o ID do produto na escrita (POST/PUT) e retorna o objeto
    aninhado na leitura (GET).

    `use_pk_only_optimization = False` é essencial: sem isso o DRF
    entrega um `PKOnlyObject` (só com `.pk`) em vez da instância real,
    e o `ProdutoNestedSerializer` falha ao acessar `.nome`.
    """

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        return ProdutoNestedSerializer(value).data


class ProdutoSerializer(serializers.ModelSerializer):
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
    produto = ProdutoRelatedField(queryset=Produto.objects.all())

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
