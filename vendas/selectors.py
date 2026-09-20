# vendas/selectors.py
from django.db.models import Prefetch
from estoque.models import Movimentacao
from .models import Pedido, ContaReceber


def get_pedidos_detalhados():
    """
    Retorna um QuerySet de todos os pedidos com relações otimizadas.

    Usa select_related para ForeignKeys (cliente, usuario) e
    prefetch_related para ManyToMany/Reverse FKs (movimentacoes, contas_receber).

    Isso evita o problema de N+1 queries ao serializar ou exibir os dados no template/admin.
    """
    return Pedido.objects.select_related("cliente", "usuario").prefetch_related(
        "contas_receber",
        Prefetch(
            "movimentacoes", queryset=Movimentacao.objects.select_related("produto")
        ),
    )


def get_pedido_detalhado_por_id(pedido_id: int):
    """
    Retorna um único pedido detalhado pelo seu ID.
    Lança Pedido.DoesNotExist se não for encontrado.
    """
    return get_pedidos_detalhados().get(id=pedido_id)


def get_pedidos_por_cliente(cliente_id: int):
    """
    Retorna todos os pedidos detalhados de um cliente específico.
    """
    return get_pedidos_detalhados().filter(cliente_id=cliente_id)


def get_pedidos_por_status(status: str):
    """
    Retorna todos os pedidos detalhados filtrados por status.
    """
    return get_pedidos_detalhados().filter(status=status)


def get_contas_receber_do_pedido(pedido_id: int):
    """
    Retorna as contas a receber de um pedido específico, já ordenadas.
    """
    return (
        ContaReceber.objects.select_related("pedido")
        .filter(pedido_id=pedido_id)
        .order_by("numero_parcela")
    )
