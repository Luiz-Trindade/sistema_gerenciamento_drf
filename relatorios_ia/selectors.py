from datetime import timedelta
from decimal import Decimal
from django.db.models import (
    Case,
    Count,
    DecimalField,
    F,
    IntegerField,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from clientes.models import Cliente
from estoque.models import Movimentacao, Produto
from vendas.models import ContaReceber, Pedido


def consultar_resumo_vendas(dias: int | None = 30) -> dict:
    """Calcula faturamento, total de pedidos e ticket médio. Se dias for None ou 0, busca todo o histórico."""
    pedidos = Pedido.objects.filter(status=Pedido.Status.CONCLUIDO)

    if dias and dias > 0:
        data_inicio = timezone.now() - timedelta(days=dias)
        pedidos = pedidos.filter(criado_em__gte=data_inicio)

    agregado = pedidos.aggregate(
        total_faturado=Coalesce(
            Sum("valor_total"),
            Value(Decimal("0.00"), output_field=DecimalField()),
        )
    )

    total_faturado = agregado["total_faturado"]
    total_pedidos = pedidos.count()
    ticket_medio = (
        (total_faturado / total_pedidos) if total_pedidos > 0 else Decimal("0.00")
    )

    return {
        "periodo_dias": dias if dias else "todo o histórico",
        "total_faturado": total_faturado,
        "total_pedidos": total_pedidos,
        "ticket_medio": ticket_medio,
    }


def consultar_principais_clientes(limite: int = 5, dias: int | None = 30) -> list[dict]:
    """Retorna os clientes que mais compraram em valor total no período."""
    pedidos = Pedido.objects.filter(
        status=Pedido.Status.CONCLUIDO, cliente__isnull=False
    )

    if dias and dias > 0:
        data_inicio = timezone.now() - timedelta(days=dias)
        pedidos = pedidos.filter(criado_em__gte=data_inicio)

    clientes = (
        pedidos.values("cliente__id", "cliente__nome")
        .annotate(
            total_gasto=Coalesce(
                Sum("valor_total"),
                Value(Decimal("0.00"), output_field=DecimalField()),
            ),
            total_pedidos=Count("id"),
        )
        .order_by("-total_gasto")[:limite]
    )

    return [
        {
            "id": c["cliente__id"],
            "nome": c["cliente__nome"],
            "total_gasto": c["total_gasto"],
            "total_pedidos": c["total_pedidos"],
        }
        for c in clientes
    ]


def consultar_produtos_mais_vendidos(
    limite: int = 5, dias: int | None = 30
) -> list[dict]:
    """Retorna os produtos mais vendidos em quantidade no período."""
    pedidos = Pedido.objects.filter(status=Pedido.Status.CONCLUIDO)

    if dias and dias > 0:
        data_inicio = timezone.now() - timedelta(days=dias)
        pedidos = pedidos.filter(criado_em__gte=data_inicio)

    movimentacoes = Movimentacao.objects.filter(
        pedidos__in=pedidos, tipo=Movimentacao.Tipo.SAIDA
    )

    produtos = (
        movimentacoes.values("produto__id", "produto__nome")
        .annotate(
            qtd_vendida=Coalesce(Sum("quantidade"), Value(0)),
            faturamento=Coalesce(
                Sum(F("quantidade") * F("produto__preco")),
                Value(Decimal("0.00"), output_field=DecimalField()),
            ),
        )
        .order_by("-qtd_vendida")[:limite]
    )

    return [
        {
            "id": p["produto__id"],
            "nome": p["produto__nome"],
            "quantidade_vendida": p["qtd_vendida"],
            "faturamento_gerado": p["faturamento"],
        }
        for p in produtos
    ]


def consultar_produtos_estoque_critico(limite_minimo: int = 5) -> list[dict]:
    """Retorna produtos ativos com saldo igual ou inferior ao limite especificado."""
    produtos = (
        Produto.objects.filter(ativo=True)
        .annotate(
            saldo=Coalesce(
                Sum(
                    Case(
                        When(
                            movimentacoes__tipo="entrada",
                            then=F("movimentacoes__quantidade"),
                        ),
                        When(
                            movimentacoes__tipo="saida",
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
        .filter(saldo__lte=limite_minimo)
        .order_by("saldo")
    )

    return [
        {
            "id": p.pk,
            "nome": p.nome,
            "saldo": p.saldo,
            "preco": p.preco,
        }
        for p in produtos
    ]


def consultar_contas_receber_proximos_dias(dias: int = 7) -> dict:
    """Retorna a previsão de recebimentos futuros e pendências financeiras."""
    hoje = timezone.localdate()
    data_limite = hoje + timedelta(days=dias)

    contas_periodo = ContaReceber.objects.filter(
        status=ContaReceber.Status.PENDENTE,
        vencimento__range=[hoje, data_limite],
    )

    contas_vencidas = ContaReceber.objects.filter(
        status=ContaReceber.Status.PENDENTE,
        vencimento__lt=hoje,
    )

    agregado_periodo = contas_periodo.aggregate(
        total_periodo=Coalesce(
            Sum("valor"),
            Value(Decimal("0.00"), output_field=DecimalField()),
        )
    )

    agregado_vencido = contas_vencidas.aggregate(
        total_vencido=Coalesce(
            Sum("valor"),
            Value(Decimal("0.00"), output_field=DecimalField()),
        )
    )

    return {
        "dias_previsao": dias,
        "total_a_receber": agregado_periodo["total_periodo"],
        "qtd_parcelas_periodo": contas_periodo.count(),
        "total_vencido": agregado_vencido["total_vencido"],
        "qtd_parcelas_vencidas": contas_vencidas.count(),
    }


def consultar_detalhes_cliente(termo_busca: str) -> list[dict]:
    """Busca um cliente por nome, CPF ou CNPJ e retorna seus dados com o histórico de pedidos."""
    clientes = Cliente.objects.filter(
        Q(nome__icontains=termo_busca)
        | Q(cpf__icontains=termo_busca)
        | Q(cnpj__icontains=termo_busca)
    )[:3]

    resultado = []
    for c in clientes:
        pedidos = c.pedidos.filter(status=Pedido.Status.CONCLUIDO)
        total_gasto = pedidos.aggregate(
            total=Coalesce(
                Sum("valor_total"), Value(Decimal("0.00"), output_field=DecimalField())
            )
        )["total"]

        resultado.append(
            {
                "id": c.pk,
                "nome": c.nome,
                "documento": c.cpf or c.cnpj or "Não informado",
                "telefone": c.telefone_1 or "Não informado",
                "email": c.email_1 or "Não informado",
                "total_compras": pedidos.count(),
                "total_gasto": total_gasto,
            }
        )

    return resultado
