# vendas/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from estoque.models import Movimentacao, Produto
from .models import Pedido


@transaction.atomic
def criar_pedido_com_itens(usuario, cliente_id, status, itens):
    """
    Cria um Pedido e suas respectivas Movimentações de Saída de forma atômica.

    :param usuario: Instância do usuário (request.user)
    :param cliente_id: ID do cliente (pode ser None se não for obrigatório)
    :param status: Status inicial do pedido (ex: 'criado')
    :param itens: Lista de dicionários [{'produto_id': int, 'quantidade': int, 'observacao': str}]
    :return: Instância do Pedido criado
    """
    if not itens:
        raise ValidationError(
            "É necessário fornecer pelo menos um item para criar o pedido."
        )

    # 1. Criar o Pedido básico
    pedido = Pedido.objects.create(
        cliente_id=cliente_id, usuario=usuario, status=status
    )

    movimentacoes_ids = []

    # 2. Processar cada item, criando a movimentação de saída
    for item in itens:
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade")
        observacao = item.get("observacao", f"Item do Pedido #{pedido.id}")

        if not produto_id or not quantidade:
            raise ValidationError("Cada item deve conter 'produto_id' e 'quantidade'.")

        # select_for_update() bloqueia a linha do produto no banco até o fim da transação,
        # evitando que dois pedidos simultâneos leiam o mesmo saldo e causem estoque negativo.
        produto = Produto.objects.select_for_update().get(id=produto_id)

        # Validação de estoque (Regra de Negócio Crucial)
        if produto.saldo_estoque < quantidade:
            raise ValidationError(
                f"Saldo insuficiente para o produto '{produto.nome}'. "
                f"Saldo atual: {produto.saldo_estoque}, Solicitado: {quantidade}"
            )

        # Cria a movimentação de saída
        mov = Movimentacao.objects.create(
            produto=produto,
            tipo=Movimentacao.Tipo.SAIDA,
            quantidade=quantidade,
            observacao=observacao,
        )
        movimentacoes_ids.append(mov.id)

    # 3. Associar as movimentações criadas ao pedido (ManyToMany)
    pedido.movimentacoes.set(movimentacoes_ids)

    # 4. Forçar a atualização do valor total (o sinal m2m_changed já faz isso,
    # mas chamar explicitamente garante a consistência imediata)
    pedido.atualizar_valor_total()

    return pedido
