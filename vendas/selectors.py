# vendas/selectors.py
from datetime import timedelta
from django.db.models import Prefetch
from django.utils import timezone
from estoque.models import Movimentacao
from .models import Pedido, ContaReceber

# ==========================================
# SELECTORS DE PEDIDOS
# ==========================================


def get_pedidos_detalhados():
    """
    Retorna um QuerySet de todos os pedidos com relações otimizadas.
    Usa select_related para ForeignKeys e prefetch_related para ManyToMany/Reverse FKs.
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


# ==========================================
# SELECTORS DE CONTAS A RECEBER
# ==========================================


def get_contas_receber_detalhadas():
    """
    Retorna um QuerySet de todas as contas a receber com relações otimizadas.
    Faz join com 'pedido' e 'pedido__cliente' para evitar N+1 queries ao exibir
    o nome do cliente na listagem.
    """
    return ContaReceber.objects.select_related("pedido", "pedido__cliente").order_by(
        "vencimento", "numero_parcela"
    )


def get_conta_receber_detalhada_por_id(conta_id: int):
    """
    Retorna uma única conta a receber detalhada pelo seu ID.
    """
    return get_contas_receber_detalhadas().get(id=conta_id)


def get_contas_receber_do_pedido(pedido_id: int):
    """
    Retorna as contas a receber de um pedido específico, já ordenadas por parcela.
    """
    return (
        ContaReceber.objects.select_related("pedido", "pedido__cliente")
        .filter(pedido_id=pedido_id)
        .order_by("numero_parcela")
    )


def get_contas_receber_por_status(status: str):
    """
    Retorna contas a receber filtradas por status (ex: 'pendente', 'paga').
    """
    return get_contas_receber_detalhadas().filter(status=status)


def get_contas_receber_por_cliente(cliente_id: int):
    """
    Retorna todas as contas a receber de um cliente específico.
    """
    return get_contas_receber_detalhadas().filter(pedido__cliente_id=cliente_id)


def get_contas_receber_vencidas():
    """
    Retorna contas a receber PENDENTES com data de vencimento anterior à data de hoje.
    """
    hoje = timezone.localdate()
    return get_contas_receber_detalhadas().filter(
        status=ContaReceber.Status.PENDENTE, vencimento__lt=hoje
    )


def get_contas_receber_a_vencer(proximos_dias: int = 30):
    """
    Retorna contas a receber PENDENTES que vencem entre hoje e a data limite (padrão: 30 dias).
    Útil para dashboards de fluxo de caixa.
    """
    hoje = timezone.localdate()
    data_limite = hoje + timedelta(days=proximos_dias)

    return get_contas_receber_detalhadas().filter(
        status=ContaReceber.Status.PENDENTE,
        vencimento__gte=hoje,
        vencimento__lte=data_limite,
    )
