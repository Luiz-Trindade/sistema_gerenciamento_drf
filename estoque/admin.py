from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Movimentacao, Produto

# ==========================================
# 1. RESOURCES
# ==========================================


class ProdutoResource(resources.ModelResource):
    class Meta:
        model = Produto
        fields = (
            "id",
            "nome",
            "descricao",
            "preco",
            "ativo",
            "criado_em",
            "atualizado_em",
        )
        export_order = fields


class MovimentacaoResource(resources.ModelResource):
    produto = fields.Field(
        column_name="produto",
        attribute="produto",
        widget=ForeignKeyWidget(Produto, field="nome"),
    )

    class Meta:
        model = Movimentacao
        fields = (
            "id",
            "produto",
            "tipo",
            "quantidade",
            "observacao",
            "criado_em",
        )
        export_order = fields


# ==========================================
# 2. ADMINS & INLINES
# ==========================================


class MovimentacaoInline(TabularInline):
    model = Movimentacao
    extra = 0
    readonly_fields = ("criado_em",)
    fields = ("tipo", "quantidade", "observacao", "criado_em")


@admin.register(Produto)
class ProdutoAdmin(SimpleHistoryAdmin, ImportExportModelAdmin, ModelAdmin):
    resource_classes = [ProdutoResource]

    list_display = ("nome", "preco", "get_saldo_estoque", "ativo", "criado_em")
    list_editable = ("ativo",)
    list_filter = ("ativo", "criado_em", "atualizado_em")
    search_fields = ("nome", "descricao")
    readonly_fields = ("get_saldo_estoque", "criado_em", "atualizado_em")
    # inlines = [MovimentacaoInline]

    # Colunas extras no histórico (opcional, mas útil)
    history_list_display = ["preco", "ativo"]

    @admin.display(description="Saldo em Estoque")
    def get_saldo_estoque(self, obj):
        return obj.saldo_estoque


@admin.register(Movimentacao)
class MovimentacaoAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_classes = [MovimentacaoResource]

    list_display = ("produto", "get_tipo_display_custom", "quantidade", "criado_em")
    list_filter = ("tipo", "criado_em")
    search_fields = ("produto__nome", "observacao")
    readonly_fields = ("criado_em",)
    autocomplete_fields = ["produto"]

    @display(
        description="Tipo",
        label={
            "Entrada": "success",  # Verde
            "Saída": "danger",  # Vermelho
        },
    )
    def get_tipo_display_custom(self, obj):
        return obj.get_tipo_display()
