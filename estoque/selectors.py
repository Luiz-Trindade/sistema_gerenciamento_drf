from typing import Optional

from django.db.models import (
    Case,
    F,
    IntegerField,
    QuerySet,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from .models import Movimentacao, Produto


class BaseSelector:
    """
    Seletor base para consultas de leitura.

    Pode receber um queryset customizado; caso contrário, usa
    `model.objects.all()`.
    """

    model = None

    def __init__(self, queryset: Optional[QuerySet] = None):
        if queryset is None:
            queryset = self.model.objects.all()
        self.queryset = queryset

    def all(self) -> QuerySet:
        """Retorna o queryset atual."""
        return self.queryset

    def get(self, **kwargs):
        """Retorna um único objeto ou 404."""
        return get_object_or_404(self.queryset, **kwargs)

    def filter(self, **kwargs) -> QuerySet:
        """Aplica filtros e retorna um novo queryset."""
        return self.queryset.filter(**kwargs)


class ProdutoSelector(BaseSelector):
    """Consultas relacionadas a Produto."""

    model = Produto

    def ativos(self) -> QuerySet:
        return self.queryset.filter(ativo=True)

    def inativos(self) -> QuerySet:
        return self.queryset.filter(ativo=False)

    def buscar(self, termo: str) -> QuerySet:
        return self.queryset.filter(nome__icontains=termo)

    def com_saldo_estoque(self) -> QuerySet:
        """
        Anota o saldo de estoque calculado.

        Usa `saldo_estoque_anotado` para não sobrescrever a property
        `saldo_estoque` do model.
        """
        return self.queryset.annotate(
            saldo_estoque_anotado=Coalesce(
                Sum(
                    Case(
                        When(
                            movimentacoes__tipo=Movimentacao.Tipo.ENTRADA,
                            then=F("movimentacoes__quantidade"),
                        ),
                        When(
                            movimentacoes__tipo=Movimentacao.Tipo.SAIDA,
                            then=-F("movimentacoes__quantidade"),
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
                Value(0),
                output_field=IntegerField(),
            )
        )


class MovimentacaoSelector(BaseSelector):
    """Consultas relacionadas a Movimentacao."""

    model = Movimentacao

    def __init__(self, queryset: Optional[QuerySet] = None):
        if queryset is None:
            queryset = Movimentacao.objects.select_related("produto")
        super().__init__(queryset)

    def por_produto(self, produto) -> QuerySet:
        return self.queryset.filter(produto=produto)

    def por_produto_id(self, produto_id: int) -> QuerySet:
        return self.queryset.filter(produto_id=produto_id)

    def por_tipo(self, tipo: str) -> QuerySet:
        return self.queryset.filter(tipo=tipo)

    def entradas(self) -> QuerySet:
        return self.por_tipo(Movimentacao.Tipo.ENTRADA)

    def saidas(self) -> QuerySet:
        return self.por_tipo(Movimentacao.Tipo.SAIDA)

    def recentes(self, limite: int = 10) -> QuerySet:
        return self.queryset[:limite]
