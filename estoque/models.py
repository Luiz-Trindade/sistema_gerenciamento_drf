from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, IntegerField, F, Sum, Value, When
from django.db.models.functions import Coalesce


class Produto(models.Model):
    """
    Representa um produto cadastrado no sistema de estoque.

    Armazena as informações básicas do produto, como nome, descrição,
    preço e situação atual. O campo `ativo` indica se o produto está
    disponível para utilização no sistema.

    O saldo em estoque não é armazenado diretamente neste model. Ele é
    calculado dinamicamente pela propriedade `saldo_estoque`, considerando
    as movimentações de entrada e saída associadas ao produto por meio do
    relacionamento `movimentacoes`.

    Attributes:
        nome: Nome utilizado para identificar o produto.
        descricao: Informações adicionais sobre o produto.
        preco: Preço unitário do produto.
        ativo: Indica se o produto está ativo no sistema.
        criado_em: Data e hora em que o produto foi cadastrado.
        atualizado_em: Data e hora da última atualização do produto.
    """

    nome = models.CharField(
        verbose_name="nome",
        max_length=255,
    )
    descricao = models.TextField(
        verbose_name="descrição",
        blank=True,
        null=True,
    )
    preco = models.DecimalField(
        verbose_name="preço",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    ativo = models.BooleanField(
        verbose_name="ativo",
        default=True,
    )
    criado_em = models.DateTimeField(
        verbose_name="criado em",
        auto_now_add=True,
    )
    atualizado_em = models.DateTimeField(
        verbose_name="atualizado em",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def saldo_estoque(self):
        """
        Retorna o saldo do produto calculado a partir das movimentações.

        Entrada: soma a quantidade.
        Saída: subtrai a quantidade.
        """
        resultado = self.movimentacoes.aggregate(
            saldo=Coalesce(
                Sum(
                    Case(
                        When(
                            tipo=Movimentacao.Tipo.ENTRADA,
                            then=F("quantidade"),
                        ),
                        When(
                            tipo=Movimentacao.Tipo.SAIDA,
                            then=-F("quantidade"),
                        ),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ),
                Value(0),
                output_field=IntegerField(),
            ),
        )
        return resultado["saldo"]


class Movimentacao(models.Model):
    """
    Representa uma movimentação de entrada ou saída no estoque.

    Cada movimentação está vinculada a um produto e registra o tipo,
    a quantidade movimentada, uma observação opcional e a data de criação.

    Movimentações de entrada aumentam o saldo do produto, enquanto
    movimentações de saída diminuem seu saldo.

    Attributes:
        produto: Produto relacionado à movimentação.
        tipo: Indica se a movimentação é uma entrada ou uma saída.
        quantidade: Quantidade movimentada do produto.
        observacao: Informação adicional sobre a movimentação.
        criado_em: Data e hora em que a movimentação foi registrada.
    """

    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SAIDA = "saida", "Saída"

    produto = models.ForeignKey(
        Produto,
        verbose_name="produto",
        on_delete=models.PROTECT,
        related_name="movimentacoes",
    )
    tipo = models.CharField(
        verbose_name="tipo",
        max_length=7,
        choices=Tipo.choices,
    )
    quantidade = models.IntegerField(
        verbose_name="quantidade",
        validators=[MinValueValidator(1)],
    )
    observacao = models.TextField(
        verbose_name="observação",
        blank=True,
        null=True,
    )
    criado_em = models.DateTimeField(
        verbose_name="criado em",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome} ({self.quantidade})"
