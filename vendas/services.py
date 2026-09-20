# vendas/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from estoque.models import Movimentacao, Produto
from .models import Pedido, ContaReceber


@transaction.atomic
def criar_pedido_com_itens(
    usuario, cliente_id, status, itens, pagar_agora=False, meio_pagamento=None
):
    """
    Cria um Pedido, suas Movimentações de Saída e uma Conta a Receber.
    Se pagar_agora=True, a conta é criada já como PAGA.
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

        produto = Produto.objects.select_for_update().get(id=produto_id)

        if produto.saldo_estoque < quantidade:
            raise ValidationError(
                f"Saldo insuficiente para o produto '{produto.nome}'. "
                f"Saldo atual: {produto.saldo_estoque}, Solicitado: {quantidade}"
            )

        mov = Movimentacao.objects.create(
            produto=produto,
            tipo=Movimentacao.Tipo.SAIDA,
            quantidade=quantidade,
            observacao=observacao,
        )
        movimentacoes_ids.append(mov.id)

    # 3. Associar as movimentações e calcular valor total
    pedido.movimentacoes.set(movimentacoes_ids)
    valor_total = pedido.atualizar_valor_total()

    # 4. Criar a Conta a Receber com validação rigorosa
    if valor_total > 0:
        conta = ContaReceber(
            pedido=pedido,
            numero_parcela=1,
            total_parcelas=1,
            valor=valor_total,
            observacao="Gerada automaticamente na criação do pedido (PDV).",
        )

        if pagar_agora and meio_pagamento:
            # Fluxo de Pagamento Imediato
            conta.status = ContaReceber.Status.PAGA
            conta.valor_pago = valor_total
            conta.meio_pagamento = meio_pagamento
            conta.pago_em = timezone.now()
            conta.vencimento = timezone.localdate()  # Vence hoje, pois já foi pago
        else:
            # Fluxo Padrão (A Prazo)
            conta.status = ContaReceber.Status.PENDENTE
            conta.valor_pago = Decimal("0.00")
            conta.meio_pagamento = None
            conta.pago_em = None
            conta.vencimento = timezone.localdate() + timedelta(days=30)

        # Garante que as regras do modelo (clean) sejam respeitadas antes de salvar
        conta.full_clean()
        conta.save()

    return pedido
