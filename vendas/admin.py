# vendas/admin.py
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError as DjangoValidationError
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .models import ContaReceber, Pedido
from .services import criar_pedido_com_itens

# ==========================================
# 1. RESOURCES
# ==========================================


class PedidoResource(resources.ModelResource):
    class Meta:
        model = Pedido
        fields = (
            "id",
            "cliente",
            "usuario",
            "status",
            "valor_total",
            "criado_em",
            "atualizado_em",
        )
        export_order = fields


class ContaReceberResource(resources.ModelResource):
    pedido = fields.Field(
        column_name="pedido",
        attribute="pedido",
        widget=ForeignKeyWidget(Pedido, field="id"),
    )

    class Meta:
        model = ContaReceber
        fields = (
            "id",
            "pedido",
            "numero_parcela",
            "total_parcelas",
            "valor",
            "vencimento",
            "status",
            "meio_pagamento",
            "valor_pago",
            "pago_em",
            "observacao",
            "criado_em",
            "atualizado_em",
        )
        export_order = fields


# ==========================================
# 2. ADMINS & INLINES
# ==========================================


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


class PedidoAdminForm(forms.ModelForm):
    itens_raw = forms.CharField(
        required=False,
        label="Adicionar Itens (Formato: ID_Produto:Quantidade)",
        help_text="Ex: 1:2, 5:1 (Cria movimentações de saída automaticamente ao salvar um NOVO pedido). Deixe em branco para gerenciar manualmente via 'Movimentações' abaixo.",
        widget=forms.TextInput(attrs={"placeholder": "ex: 1:2, 3:1"}),
    )

    class Meta:
        model = Pedido
        fields = "__all__"

    def save(self, commit=True):
        # Se for um novo pedido (sem PK) e o campo de itens foi preenchido
        if not self.instance.pk and self.cleaned_data.get("itens_raw"):
            itens_input = self.cleaned_data["itens_raw"]
            itens = []

            # Parse simples do formato "id:qtd, id:qtd"
            for parte in itens_input.split(","):
                parte = parte.strip()
                if ":" in parte:
                    prod_id, qtd = parte.split(":")
                    itens.append(
                        {
                            "produto_id": int(prod_id.strip()),
                            "quantidade": int(qtd.strip()),
                        }
                    )

            if itens:
                # Usa o mesmo serviço unificado!
                return criar_pedido_com_itens(
                    usuario=self.cleaned_data["usuario"],
                    cliente_id=(
                        self.cleaned_data["cliente"].id
                        if self.cleaned_data["cliente"]
                        else None
                    ),
                    status=self.cleaned_data["status"],
                    itens=itens,
                )

        # Comportamento padrão do Django (para edições ou quando itens_raw está vazio)
        return super().save(commit=commit)


@admin.register(Pedido)
class PedidoAdmin(ModelAdmin, ImportExportModelAdmin):
    form = PedidoAdminForm
    resource_classes = [PedidoResource]
    import_form_class = ImportForm
    export_form_class = ExportForm

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
        ("Criação Rápida de Itens", {"fields": ("itens_raw",)}),
        (
            "Itens do Pedido (Avançado)",
            {"fields": ("movimentacoes",), "classes": ("collapse",)},
        ),
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

    # ==========================================
    # MÉTODOS CUSTOMIZADOS PARA LIST_DISPLAY E READONLY_FIELDS
    # ==========================================

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
            valor_formatado = f"R$ {valor:.2f}".replace(".", ",")
            # mark_safe é a forma mais segura e compatível de retornar HTML customizado no Admin
            return mark_safe(
                f'<span class="text-red-600 font-semibold">{valor_formatado}</span>'
            )
        return f"R$ {valor:.2f}".replace(".", ",")


@admin.register(ContaReceber)
class ContaReceberAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_classes = [ContaReceberResource]
    import_form_class = ImportForm
    export_form_class = ExportForm

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
