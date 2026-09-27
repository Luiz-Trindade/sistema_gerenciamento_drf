# vendas/migrations/0002_seed_dados_teste.py
"""
Migração de dados: popula o banco com dados de teste realistas
(clientes, movimentações de estoque, pedidos de venda e contas a receber)
cobrindo cerca de 120 dias (~4 meses) de operação.

Correções em relação à versão anterior:
    - Estoque nunca fica negativo: mantemos um contador de estoque em
      memória por produto. Toda "saída" é limitada ao que existe em
      estoque no momento (e o pedido só usa produtos com saldo > 0).
    - Produtos acabados agora recebem "entradas" (produção semanal),
      já que antes só matéria-prima entrava e produto acabado só saía
      — isso é o que gerava estoque negativo.
    - Período aumentado de 100 para 120 dias, garantindo com folga
      pedidos "concluído" distribuídos por mais de 3 meses.
    - Pedidos não são mais criados em finais de semana (mais realista).
    - Mais produtos acabados e clientes para enriquecer a base.

Marcadores utilizados para permitir reversão segura:
    - clientes: e-mails terminando em "@seed.local"
    - movimentações e contas: observação contendo "[seed]"
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import migrations
from django.utils import timezone

SEED_SUFFIX = "@seed.local"
SEED_OBS = "[seed]"

DIAS_HISTORICO = 120  # ~4 meses, com folga confortável acima de 3 meses


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _aware(date_value, hour=12, minute=0):
    """Converte uma `date` em `datetime` ciente do fuso (se USE_TZ=True)."""
    naive = datetime.combine(date_value, datetime.min.time()).replace(
        hour=hour, minute=minute
    )
    if settings.USE_TZ:
        return timezone.make_aware(naive, timezone.get_current_timezone())
    return naive


def _backdate(model, pk, criado_em, **extra):
    """Atualiza campos com auto_now/auto_now_add via queryset.update()."""
    dados = {"criado_em": criado_em}
    dados.update(extra)
    model.objects.filter(pk=pk).update(**dados)


# ---------------------------------------------------------------------------
# Forward
# ---------------------------------------------------------------------------
def popular_dados_teste(apps, schema_editor):
    Produto = apps.get_model("estoque", "Produto")
    Movimentacao = apps.get_model("estoque", "Movimentacao")
    Cliente = apps.get_model("clientes", "Cliente")
    Pedido = apps.get_model("vendas", "Pedido")
    ContaReceber = apps.get_model("vendas", "ContaReceber")
    # Em data migrations o correto é usar o registro histórico `apps`,
    # e não `get_user_model()`, para respeitar o estado da migração.
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    # Idempotência: se já rodou uma vez, não duplica.
    if Cliente.objects.filter(email__endswith=SEED_SUFFIX).exists():
        return

    # ---------------------------------------------------------------- Usuário
    # O AUTH_USER_MODEL do projeto NÃO possui campo `username`
    # (login por e-mail). A senha "!" marca a senha como inutilizável,
    # impedindo login do usuário de seed.
    usuario, _ = User.objects.get_or_create(
        email="seed@example.com",
        defaults={
            "first_name": "Seed",
            "is_staff": True,
            "is_active": True,
            "password": "!",
        },
    )

    rng = random.Random(20240101)
    hoje = timezone.localdate()
    inicio = hoje - timedelta(days=DIAS_HISTORICO)

    # --------------------------------------------------------------- Produtos
    dados_produtos = [
        ("Ácido FE 40 01 LT", "Matéria Prima", "40.00"),
        ("Ácido Clorídrico", "Matéria Prima", "25.00"),
        ("Ácido Sulfônico", "Matéria Prima", "50.00"),
        ("Soda Cáustica 01 KG", "Matéria Prima", "20.00"),
        ("Lauril 01 LT", "Matéria Prima", "15.00"),
        ("Cloreto de Sódio 25 KG", "Matéria Prima", "18.00"),
        ("Essência Perfumada 01 LT", "Matéria Prima", "35.00"),
        ("Shampoo 05 LTS", "Produto Acabado", "25.00"),
        ("Desengraxante 1L", "Produto Acabado", "25.00"),
        ("L. Alumínio 05 LTS", "Produto Acabado (Limpa Alumínio)", "25.00"),
        ("Silicone Gel 500 GR", "Produto Acabado", "15.00"),
        ("L. Pneus 500 GR", "Produto Acabado (Limpa Pneus)", "10.00"),
        ("Sintra 01 LT", "Produto Acabado", "10.00"),
        ("Vaselina Líquida", "Produto Acabado", "30.00"),
        ("Cloro", "1L", "5.75"),
        ("Amaciante 05 LTS", "Produto Acabado", "22.00"),
        ("Detergente Neutro 05 LTS", "Produto Acabado", "18.00"),
        ("Fictício", "Bla bla", "20.00"),
    ]

    produtos_por_nome = {}
    for nome, descricao, preco in dados_produtos:
        obj, _ = Produto.objects.get_or_create(
            nome=nome,
            defaults={
                "descricao": descricao,
                "preco": Decimal(preco),
                "ativo": True,
            },
        )
        produtos_por_nome[nome] = obj

    todos_produtos = list(produtos_por_nome.values())
    materias_primas = [
        p for p in todos_produtos if (p.descricao or "").startswith("Matéria Prima")
    ] or todos_produtos
    produtos_acabados = [
        p for p in todos_produtos if (p.descricao or "").startswith("Produto Acabado")
    ] or todos_produtos

    # --------------------------------------------------------------- Clientes
    clientes_seed = [
        {
            "nome": "Ana Beatriz Souza",
            "email": f"ana.souza{SEED_SUFFIX}",
            "telefone": "(11) 98765-4321",
            "cpf": "123.456.789-01",
        },
        {
            "nome": "Bruno Carvalho",
            "email": f"bruno.carvalho{SEED_SUFFIX}",
            "telefone": "(11) 99876-5432",
            "cpf": "234.567.890-12",
        },
        {
            "nome": "Carla Menezes",
            "email": f"carla.menezes{SEED_SUFFIX}",
            "telefone": "(21) 98888-7777",
            "cpf": "345.678.901-23",
        },
        {
            "nome": "Diego Almeida",
            "email": f"diego.almeida{SEED_SUFFIX}",
            "telefone": "(31) 97777-6666",
            "cpf": "456.789.012-34",
        },
        {
            "nome": "Eduarda Lima",
            "email": f"eduarda.lima{SEED_SUFFIX}",
            "telefone": "(41) 96666-5555",
            "cpf": "567.890.123-45",
        },
        {
            "nome": "Fábio Nogueira",
            "email": f"fabio.nogueira{SEED_SUFFIX}",
            "telefone": "(51) 95555-4444",
            "cpf": "678.901.234-56",
        },
        {
            "nome": "Gisele Rocha",
            "email": f"gisele.rocha{SEED_SUFFIX}",
            "telefone": "(61) 94444-3333",
            "cpf": "789.012.345-67",
        },
        {
            "nome": "Henrique Pires",
            "email": f"henrique.pires{SEED_SUFFIX}",
            "telefone": "(71) 93333-2222",
            "cpf": "890.123.456-78",
        },
        {
            "nome": "Isabela Martins",
            "email": f"isabela.martins{SEED_SUFFIX}",
            "telefone": "(81) 92222-1111",
            "cpf": "901.234.567-89",
        },
        {
            "nome": "João Pedro Ramos",
            "email": f"joao.ramos{SEED_SUFFIX}",
            "telefone": "(91) 91111-0000",
            "cpf": "012.345.678-90",
        },
        {
            "nome": "Karina Duarte",
            "email": f"karina.duarte{SEED_SUFFIX}",
            "telefone": "(19) 98123-4567",
            "cpf": "112.233.445-56",
        },
        {
            "nome": "Leonardo Freitas",
            "email": f"leonardo.freitas{SEED_SUFFIX}",
            "telefone": "(27) 97123-4567",
            "cpf": "223.344.556-67",
        },
        {
            "nome": "Distribuidora Limpa Tudo LTDA",
            "email": f"contato.limpatudo{SEED_SUFFIX}",
            "telefone": "(11) 3333-4444",
            "cnpj": "12.345.678/0001-90",
        },
        {
            "nome": "Comercial Brilho ME",
            "email": f"contato.brilho{SEED_SUFFIX}",
            "telefone": "(21) 2222-3333",
            "cnpj": "98.765.432/0001-10",
        },
        {
            "nome": "Química Santarém Ltda",
            "email": f"contato.santarem{SEED_SUFFIX}",
            "telefone": "(91) 3222-1100",
            "cnpj": "23.456.789/0001-21",
        },
    ]

    clientes = []
    for dados in clientes_seed:
        cliente, _ = Cliente.objects.get_or_create(
            email=dados["email"],
            defaults={**dados, "ativo": True},
        )
        clientes.append(cliente)

    # ---------------------------------------------------------- Controle de estoque
    # Contador em memória usado só durante a geração dos dados, para
    # garantir que nenhuma "saída" seja criada sem saldo suficiente.
    estoque_atual = {p.pk: 0 for p in todos_produtos}

    def registrar_entrada(produto, quantidade, dt, observacao):
        estoque_atual[produto.pk] += quantidade
        mov = Movimentacao.objects.create(
            produto=produto,
            tipo="entrada",
            quantidade=quantidade,
            observacao=f"{SEED_OBS} {observacao}",
        )
        _backdate(Movimentacao, mov.pk, dt)
        return mov

    def registrar_saida(produto, quantidade, dt, observacao):
        # Nunca deixa o estoque ficar negativo: limita a quantidade
        # disponível no momento.
        disponivel = estoque_atual.get(produto.pk, 0)
        quantidade = min(quantidade, disponivel)
        if quantidade <= 0:
            return None
        estoque_atual[produto.pk] -= quantidade
        mov = Movimentacao.objects.create(
            produto=produto,
            tipo="saida",
            quantidade=quantidade,
            observacao=f"{SEED_OBS} {observacao}",
        )
        _backdate(Movimentacao, mov.pk, dt)
        return mov

    # ------------------------------------------------------- Loop semanal
    # Cada semana: primeiro entram matéria-prima e produção de produto
    # acabado (garantindo saldo), só depois são gerados os pedidos que
    # consomem esse saldo.
    dia = inicio
    numero_pedido = 0
    while dia <= hoje:
        dt_semana = _aware(dia, rng.randint(7, 9), rng.randint(0, 59))

        # Entradas de matéria-prima
        for _ in range(rng.randint(1, 3)):
            produto = rng.choice(materias_primas)
            quantidade = rng.choice([10, 20, 30, 50, 100, 150])
            dt = _aware(dia, rng.randint(7, 10), rng.randint(0, 59))
            registrar_entrada(produto, quantidade, dt, "Compra de matéria-prima")

        # Produção semanal de produtos acabados (antes só existia saída,
        # o que forçava estoque negativo — este é o principal ajuste)
        for _ in range(rng.randint(1, 2)):
            produto = rng.choice(produtos_acabados)
            quantidade = rng.choice([20, 40, 60, 80, 100])
            dt = _aware(dia, rng.randint(10, 12), rng.randint(0, 59))
            registrar_entrada(produto, quantidade, dt, "Produção")

        # Pedidos de venda da semana (pulando finais de semana)
        for _ in range(rng.randint(2, 4)):
            data_pedido = dia + timedelta(days=rng.randint(0, 6))
            if data_pedido > hoje or data_pedido.weekday() >= 5:
                continue

            # Escolhe até 3 produtos distintos com saldo em estoque
            candidatos = [
                p for p in produtos_acabados if estoque_atual.get(p.pk, 0) > 0
            ]
            if not candidatos:
                continue  # sem estoque disponível nesta semana, pula o pedido

            n_itens = rng.randint(1, min(3, len(candidatos)))
            itens = rng.sample(candidatos, k=n_itens)

            cliente = rng.choice(clientes)
            dt_pedido = _aware(data_pedido, rng.randint(13, 18), rng.randint(0, 59))

            pedido = Pedido.objects.create(
                cliente=cliente,
                usuario=usuario,
                status="concluido",
                valor_total=Decimal("0.00"),
            )
            _backdate(Pedido, pedido.pk, dt_pedido)

            valor_total = Decimal("0.00")
            algum_item_confirmado = False

            for produto in itens:
                quantidade_desejada = rng.randint(1, 5)
                mov = registrar_saida(
                    produto,
                    quantidade_desejada,
                    dt_pedido,
                    f"Saída do pedido #{numero_pedido + 1}",
                )
                if mov is None:
                    continue
                pedido.movimentacoes.add(mov)
                valor_total += produto.preco * mov.quantidade
                algum_item_confirmado = True

            if not algum_item_confirmado:
                # Nenhum item pôde ser atendido (estoque zerou entre a
                # seleção e o consumo) — descarta o pedido vazio.
                pedido.delete()
                continue

            numero_pedido += 1
            Pedido.objects.filter(pk=pedido.pk).update(valor_total=valor_total)

            # ------------------------------------------------- Parcelamento
            if valor_total >= Decimal("300.00"):
                n_parcelas = 3
            elif valor_total >= Decimal("120.00"):
                n_parcelas = 2
            else:
                n_parcelas = 1

            valor_parcela = (valor_total / n_parcelas).quantize(Decimal("0.01"))
            sobra = valor_total - (valor_parcela * n_parcelas)
            dias_desde = (hoje - data_pedido).days

            for i in range(1, n_parcelas + 1):
                vencimento = data_pedido + timedelta(days=30 * i)
                valor_parcela_atual = valor_parcela + (
                    sobra if i == n_parcelas else Decimal("0.00")
                )
                if valor_parcela_atual <= Decimal("0.00"):
                    continue

                # Define status com base na idade da conta
                if vencimento <= hoje:
                    if dias_desde >= 90:
                        status = "paga"
                    elif dias_desde >= 60:
                        status = "paga" if rng.random() < 0.85 else "pendente"
                    elif dias_desde >= 30:
                        status = "paga" if rng.random() < 0.60 else "pendente"
                    else:
                        status = "paga" if rng.random() < 0.30 else "pendente"
                else:
                    status = (
                        "paga"
                        if (dias_desde > 45 and rng.random() < 0.5)
                        else "pendente"
                    )

                # Pequena fração de canceladas antigas
                if status == "pendente" and dias_desde > 60 and rng.random() < 0.10:
                    status = "cancelada"

                conta = ContaReceber.objects.create(
                    pedido=pedido,
                    numero_parcela=i,
                    total_parcelas=n_parcelas,
                    valor=valor_parcela_atual,
                    valor_pago=Decimal("0.00"),
                    vencimento=vencimento,
                    status=status,
                    observacao=SEED_OBS,
                )

                extras = {"criado_em": dt_pedido}
                if status == "paga":
                    meio = rng.choice(
                        [
                            "dinheiro",
                            "pix",
                            "cartao_debito",
                            "cartao_credito",
                            "boleto",
                            "transferencia",
                        ]
                    )
                    # Pagamento em algum momento entre o pedido e hoje
                    offset_max = max(1, min(dias_desde, 30))
                    pago_em = _aware(
                        data_pedido + timedelta(days=rng.randint(1, offset_max)),
                        rng.randint(9, 18),
                        rng.randint(0, 59),
                    )
                    extras.update(
                        {
                            "valor_pago": valor_parcela_atual,
                            "meio_pagamento": meio,
                            "pago_em": pago_em,
                        }
                    )

                ContaReceber.objects.filter(pk=conta.pk).update(**extras)

        dia += timedelta(days=7)


# ---------------------------------------------------------------------------
# Reverse
# ---------------------------------------------------------------------------
def remover_dados_teste(apps, schema_editor):
    Movimentacao = apps.get_model("estoque", "Movimentacao")
    Cliente = apps.get_model("clientes", "Cliente")
    Pedido = apps.get_model("vendas", "Pedido")
    ContaReceber = apps.get_model("vendas", "ContaReceber")

    ContaReceber.objects.filter(observacao__contains=SEED_OBS).delete()
    Pedido.objects.filter(cliente__email__endswith=SEED_SUFFIX).delete()
    Movimentacao.objects.filter(observacao__contains=SEED_OBS).delete()
    Cliente.objects.filter(email__endswith=SEED_SUFFIX).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("estoque", "0002_historicalproduto"),
        ("clientes", "0003_cliente_descricao"),
        ("vendas", "0003_pedido_cliente"),
    ]

    operations = [
        migrations.RunPython(popular_dados_teste, remover_dados_teste),
    ]
