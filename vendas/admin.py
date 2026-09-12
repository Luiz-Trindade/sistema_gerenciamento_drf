from django.contrib import admin
from django.utils.html import format_html
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
        "get_cliente",
        "usuario",
        "status",
        "valor_total",
        "get_valor_pendente",
        "criado_em",
    )
    list_filter = ("status", "criado_em", "usuario")
    search_fields = (
        "id",
        "cliente__nome",
        "cliente__email",
        "usuario__email",
        "usuario__first_name",
    )

    filter_horizontal = ("movimentacoes",)

    readonly_fields = (
        "valor_total",
        "get_quantidade_total",
        "get_valor_recebido",
        "get_valor_pendente",
        "criado_em",
        "atualizado_em",
    )
    autocomplete_fields = ["cliente", "usuario"]

    inlines = [ContaReceberInline]

    fieldsets = (
        (None, {"fields": ("cliente", "usuario", "status")}),
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

    @admin.display(description="Cliente", ordering="cliente__nome")
    def get_cliente(self, obj):
        return obj.cliente.nome if obj.cliente else "Sem cliente"

    @admin.display(description="Qtd. Itens")
    def get_quantidade_total(self, obj):
        return obj.quantidade_total

    @admin.display(description="Valor Recebido")
    def get_valor_recebido(self, obj):
        return f"R$ {obj.valor_recebido:.2f}".replace(".", ",")

    @admin.display(description="Valor Pendente")
    def get_valor_pendente(self, obj):
        valor = obj.valor_pendente
        if valor > 0:
            return format_html(
                '<span class="text-red-600 font-semibold">R$ {:.2f}</span>'.format(
                    valor
                ).replace(".", ",")
            )
        return f"R$ {valor:.2f}".replace(".", ",")


@admin.register(ContaReceber)
class ContaReceberAdmin(ModelAdmin):
    list_display = (
        "__str__",
        "get_cliente",
        "pedido",
        "valor",
        "vencimento",
        "status",
        "meio_pagamento",
    )
    list_filter = ("status", "meio_pagamento", "vencimento")
    search_fields = ("pedido__id", "pedido__cliente__nome", "observacao")
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

    @admin.display(description="Cliente", ordering="pedido__cliente__nome")
    def get_cliente(self, obj):
        if obj.pedido and obj.pedido.cliente:
            return obj.pedido.cliente.nome
        return "Sem cliente"
