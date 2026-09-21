# dashboards/selectors.py

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db.models import (
    Case,
    When,
    F,
    Value,
    Sum,
    Count,
    DecimalField,
    IntegerField,
)
from django.db.models.functions import Coalesce, TruncMonth

from clientes.models import Cliente
from estoque.models import Produto, Movimentacao
from vendas.models import ContaReceber, Pedido


@dataclass
class DashboardFilters:
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class DashboardSelectors:
    """
    Encapsula as regras de negócio e consultas para o dashboard principal.
    Utiliza os filtros fornecidos para restringir os querysets base.
    """

    def __init__(self, filters: Optional[DashboardFilters] = None):
        self.filters = filters or DashboardFilters()
        self._pedidos_qs = None
        self._contas_qs = None

    @property
    def pedidos_qs(self):
        if self._pedidos_qs is None:
            qs = Pedido.objects.all()
            if self.filters.start_date:
                qs = qs.filter(criado_em__date__gte=self.filters.start_date)
            if self.filters.end_date:
                qs = qs.filter(criado_em__date__lte=self.filters.end_date)
            self._pedidos_qs = qs
        return self._pedidos_qs

    @property
    def contas_qs(self):
        if self._contas_qs is None:
            self._contas_qs = ContaReceber.objects.filter(pedido__in=self.pedidos_qs)
        return self._contas_qs

    # ==========================================
    # KPIs
    # ==========================================

    def get_kpi_vendas(self) -> Decimal:
        """Soma do valor total de pedidos concluídos no período."""
        result = self.pedidos_qs.filter(status=Pedido.Status.CONCLUIDO).aggregate(
            total=Coalesce(Sum("valor_total"), Decimal("0.00"))
        )
        return result["total"]

    def get_kpi_ticket_medio(self) -> Decimal:
        """Valor total de vendas concluídas dividido pela quantidade de pedidos concluídos."""
        concluidos = self.pedidos_qs.filter(status=Pedido.Status.CONCLUIDO)
        total = concluidos.aggregate(
            total=Coalesce(Sum("valor_total"), Decimal("0.00"))
        )["total"]
        count = concluidos.count()
        return (total / count) if count > 0 else Decimal("0.00")

    def get_kpi_clientes(self) -> int:
        """Quantidade de clientes distintos que realizaram pedidos no período."""
        return (
            self.pedidos_qs.filter(cliente__isnull=False)
            .values("cliente")
            .distinct()
            .count()
        )

    def get_kpi_pedidos(self) -> int:
        """Quantidade total de pedidos no período."""
        return self.pedidos_qs.count()

    def get_kpi_a_receber(self) -> Decimal:
        """Soma dos valores pendentes (valor - valor_pago) das contas a receber."""
        result = self.contas_qs.filter(status=ContaReceber.Status.PENDENTE).aggregate(
            total=Coalesce(
                Sum(F("valor") - F("valor_pago")),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        return result["total"]

    def get_kpi_estoque_baixo(self, limite: int = 5) -> int:
        """Quantidade de produtos ativos com saldo em estoque maior que 0 e menor que o limite."""
        produtos = (
            Produto.objects.filter(ativo=True)
            .annotate(
                saldo=Coalesce(
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
            .filter(saldo__lt=limite, saldo__gt=0)
        )

        return produtos.count()

    # ==========================================
    # Gráficos
    # ==========================================

    def get_evolucao_vendas(self) -> dict:
        """Evolução do valor de vendas concluídas agrupado por mês."""
        qs = (
            self.pedidos_qs.filter(status=Pedido.Status.CONCLUIDO)
            .annotate(periodo=TruncMonth("criado_em"))
            .values("periodo")
            .annotate(total=Sum("valor_total"))
            .order_by("periodo")
        )

        return {
            "labels": [item["periodo"].strftime("%b/%y") for item in qs],
            "data": [float(item["total"]) for item in qs],
        }

    def get_top_produtos(self, limit: int = 5) -> dict:
        """Top produtos mais vendidos (por quantidade) no período."""
        qs = (
            Movimentacao.objects.filter(
                tipo=Movimentacao.Tipo.SAIDA, pedidos__in=self.pedidos_qs
            )
            .values("produto__nome")
            .annotate(total=Sum("quantidade"))
            .order_by("-total")[:limit]
        )

        return {
            "labels": [item["produto__nome"] for item in qs],
            "data": [item["total"] for item in qs],
        }

    def get_meios_pagamento(self) -> dict:
        """Distribuição de meios de pagamento das contas pagas no período."""
        qs = (
            self.contas_qs.filter(status=ContaReceber.Status.PAGA)
            .values("meio_pagamento")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        choices = dict(ContaReceber.MeioPagamento.choices)
        return {
            "labels": [
                choices.get(item["meio_pagamento"], item["meio_pagamento"])
                for item in qs
            ],
            "data": [item["total"] for item in qs],
        }

    def get_pedidos_por_status(self) -> dict:
        """Distribuição de pedidos por status no período."""
        qs = (
            self.pedidos_qs.values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

        choices = dict(Pedido.Status.choices)
        return {
            "labels": [choices.get(item["status"], item["status"]) for item in qs],
            "data": [item["total"] for item in qs],
        }
