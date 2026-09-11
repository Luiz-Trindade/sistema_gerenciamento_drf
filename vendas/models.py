from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import DecimalField, F, Sum, Value
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.models.functions import Coalesce
from django.utils import timezone


class Pedido(models.Model):
    class Status(models.TextChoices):
        CRIADO = "criado", "Criado"
        PROCESSANDO = "processando", "Processando"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="usuário responsável",
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    movimentacoes = models.ManyToManyField(
        "estoque.Movimentacao",
        verbose_name="movimentações",
        related_name="pedidos",
    )
    status = models.CharField(
        verbose_name="status",
        max_length=20,
        choices=Status.choices,
        default=Status.CRIADO,
    )
    valor_total = models.DecimalField(
        verbose_name="valor total",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    criado_em = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField(verbose_name="atualizado em", auto_now=True)

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["status", "criado_em"], name="pedido_status_data_idx"),
        ]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.get_status_display()}"

    @property
    def produtos(self):
        from estoque.models import Produto

        if not self.pk:
            return Produto.objects.none()
        return Produto.objects.filter(movimentacoes__pedidos=self).distinct()

    @property
    def quantidade_total(self):
        if not self.pk:
            return 0
        return self.movimentacoes.aggregate(
            total=Coalesce(Sum("quantidade"), Value(0))
        )["total"]

    def calcular_valor_total(self):
        if not self.pk:
            return Decimal("0.00")

        resultado = self.movimentacoes.annotate(
            subtotal=F("quantidade") * F("produto__preco")
        ).aggregate(
            total=Coalesce(
                Sum("subtotal"),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)),
            )
        )
        return resultado["total"]

    def atualizar_valor_total(self):
        """Calcula, atualiza o campo e salva apenas o valor_total no banco."""
        if self.pk:
            self.valor_total = self.calcular_valor_total()
            Pedido.objects.filter(pk=self.pk).update(valor_total=self.valor_total)
        return self.valor_total

    def save(self, *args, **kwargs):
        # Garante que o objeto tenha ID antes de calcular relações M2M
        super().save(*args, **kwargs)
        # Atualiza o valor total logo após salvar a instância básica
        if self.pk:
            self.atualizar_valor_total()

    def validar_movimentacoes(self):
        if not self.pk or not self.movimentacoes.exists():
            raise ValidationError("O pedido deve possuir pelo menos uma movimentação.")

        if self.movimentacoes.exclude(tipo="saida").exists():
            raise ValidationError(
                "Um pedido deve possuir somente movimentações de saída."
            )

        if (
            self.movimentacoes.filter(pedidos__isnull=False)
            .exclude(pedidos=self)
            .exists()
        ):
            raise ValidationError(
                "Uma ou mais movimentações já pertencem a outro pedido."
            )

    @property
    def valor_recebido(self):
        return self.contas_receber.filter(status=ContaReceber.Status.PAGA).aggregate(
            total=Coalesce(
                Sum("valor_pago"),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)),
            )
        )["total"]

    @property
    def valor_pendente(self):
        return max(self.valor_total - self.valor_recebido, Decimal("0.00"))


# Sinalizador para recalcular o valor do pedido sempre que itens (movimentações) forem adicionados ou removidos no Admin
@receiver(m2m_changed, sender=Pedido.movimentacoes.through)
def atualizar_total_pedido_m2m(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.atualizar_valor_total()


class ContaReceber(models.Model):
    # O restante da classe ContaReceber continua exatamente igual...
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        PAGA = "paga", "Paga"
        CANCELADA = "cancelada", "Cancelada"

    class MeioPagamento(models.TextChoices):
        DINHEIRO = "dinheiro", "Dinheiro"
        PIX = "pix", "Pix"
        CARTAO_DEBITO = "cartao_debito", "Cartão de débito"
        CARTAO_CREDITO = "cartao_credito", "Cartão de crédito"
        BOLETO = "boleto", "Boleto"
        TRANSFERENCIA = "transferencia", "Transferência bancária"
        OUTRO = "outro", "Outro"

    pedido = models.ForeignKey(
        Pedido,
        verbose_name="pedido",
        on_delete=models.PROTECT,
        related_name="contas_receber",
    )
    numero_parcela = models.PositiveIntegerField(
        verbose_name="número da parcela",
        default=1,
        validators=[MinValueValidator(1)],
    )
    total_parcelas = models.PositiveIntegerField(
        verbose_name="total de parcelas",
        default=1,
        validators=[MinValueValidator(1)],
    )
    valor = models.DecimalField(
        verbose_name="valor",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    valor_pago = models.DecimalField(
        verbose_name="valor pago",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    vencimento = models.DateField(verbose_name="vencimento")
    meio_pagamento = models.CharField(
        verbose_name="meio de pagamento",
        max_length=20,
        choices=MeioPagamento.choices,
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name="status",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    pago_em = models.DateTimeField(verbose_name="pago em", null=True, blank=True)
    observacao = models.TextField(verbose_name="observação", blank=True)
    criado_em = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField(verbose_name="atualizado em", auto_now=True)

    class Meta:
        verbose_name = "conta a receber"
        verbose_name_plural = "contas a receber"
        ordering = ["vencimento", "numero_parcela"]
        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "numero_parcela"],
                name="parcela_unica_por_pedido",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "vencimento"], name="conta_status_venc_idx"),
            models.Index(
                fields=["pedido", "numero_parcela"], name="conta_pedido_parc_idx"
            ),
        ]

    def __str__(self):
        return f"Pedido #{self.pedido_id} | Parcela {self.numero_parcela}/{self.total_parcelas} - {self.get_status_display()}"

    @property
    def esta_vencida(self):
        if not self.vencimento:
            return False
        return (
            self.status == self.Status.PENDENTE
            and self.vencimento < timezone.localdate()
        )

    @property
    def valor_restante(self):
        valor = self.valor or Decimal("0.00")
        valor_pago = self.valor_pago or Decimal("0.00")
        return max(valor - valor_pago, Decimal("0.00"))

    def clean(self):
        super().clean()
        erros = {}
        valor = self.valor or Decimal("0.00")
        valor_pago = self.valor_pago or Decimal("0.00")

        if (
            self.numero_parcela
            and self.total_parcelas
            and self.numero_parcela > self.total_parcelas
        ):
            erros["numero_parcela"] = (
                "A parcela não pode ser maior que o total de parcelas."
            )

        if valor_pago > valor:
            erros["valor_pago"] = (
                "O valor pago não pode exceder o valor original da parcela."
            )

        if self.status == self.Status.PAGA:
            if not self.meio_pagamento:
                erros["meio_pagamento"] = "Parcelas pagas exigem meio de pagamento."
            if valor_pago != valor:
                erros["valor_pago"] = (
                    "Para marcar como paga, o valor recebido deve ser integral."
                )

        if erros:
            raise ValidationError(erros)

    @transaction.atomic
    def registrar_pagamento(self, meio_pagamento):
        if self.status == self.Status.CANCELADA:
            raise ValidationError("Conta cancelada não pode ser paga.")
        if self.status == self.Status.PAGA:
            raise ValidationError("Esta conta já encontra-se paga.")
        if meio_pagamento not in self.MeioPagamento.values:
            raise ValidationError("Meio de pagamento inválido.")

        self.meio_pagamento = meio_pagamento
        self.valor_pago = self.valor
        self.status = self.Status.PAGA
        self.pago_em = timezone.now()

        self.full_clean()
        self.save(
            update_fields=[
                "meio_pagamento",
                "valor_pago",
                "status",
                "pago_em",
                "atualizado_em",
            ]
        )

    def cancelar(self):
        if self.status == self.Status.PAGA:
            raise ValidationError("Contas pagas não podem ser canceladas.")

        self.status = self.Status.CANCELADA
        self.save(update_fields=["status", "atualizado_em"])
