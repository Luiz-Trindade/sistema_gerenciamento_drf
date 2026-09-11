from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import ContaReceber, Pedido


class ContaReceberInline(TabularInline):
    model = ContaReceber
    extra = 0
    readonly_fields = ("criado_em", "atualizado_em", "pago_em")
    fields = (
        "numero_parcela",
        "total_parcelas",
        "valor",
        "vencimento",
        "status",
        "meio_pagamento",
        "valor_pago",
        "pago_em",
    )


@admin.register(Pedido)
class PedidoAdmin(ModelAdmin):
    list_display = (
        "__str__",
        "usuario",
        "status",
        "valor_total",
        "get_valor_pendente",
        "criado_em",
    )
    list_filter = ("status", "criado_em", "usuario")
    search_fields = ("id", "usuario__email", "usuario__first_name")

    # Campo M2M usando a renderização nativa bacana do Django/Unfold
    filter_horizontal = ("movimentacoes",)

    readonly_fields = (
        "valor_total",
        "get_quantidade_total",
        "get_valor_recebido",
        "get_valor_pendente",
        "criado_em",
        "atualizado_em",
    )
    autocomplete_fields = ["usuario"]
    inlines = [ContaReceberInline]

    fieldsets = (
        (None, {"fields": ("usuario", "status")}),
        ("Itens do Pedido", {"fields": ("movimentacoes",)}),
        (
            "Valores Calculados",
            {
                "fields": (
                    "valor_total",
                    "get_valor_recebido",
                    "get_valor_pendente",
                    "get_quantidade_total",
                ),
                "classes": ("tab",),
            },
        ),
        (
            "Auditoria",
            {"fields": ("criado_em", "atualizado_em"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Qtd. Itens")
    def get_quantidade_total(self, obj):
        return obj.quantidade_total

    @admin.display(description="Valor Recebido")
    def get_valor_recebido(self, obj):
        return obj.valor_recebido

    @admin.display(description="Valor Pendente")
    def get_valor_pendente(self, obj):
        return obj.valor_pendente


@admin.register(ContaReceber)
class ContaReceberAdmin(ModelAdmin):
    list_display = (
        "__str__",
        "pedido",
        "valor",
        "vencimento",
        "status",
        "meio_pagamento",
    )
    list_filter = ("status", "meio_pagamento", "vencimento")
    search_fields = ("pedido__id", "observacao")
    readonly_fields = ("criado_em", "atualizado_em")
    autocomplete_fields = ["pedido"]

    fieldsets = (
        (
            "Informações da Parcela",
            {
                "fields": (
                    "pedido",
                    "numero_parcela",
                    "total_parcelas",
                    "valor",
                    "vencimento",
                )
            },
        ),
        (
            "Pagamento",
            {"fields": ("status", "meio_pagamento", "valor_pago", "pago_em")},
        ),
        (
            "Outros",
            {
                "fields": ("observacao", "criado_em", "atualizado_em"),
                "classes": ("collapse",),
            },
        ),
    )
