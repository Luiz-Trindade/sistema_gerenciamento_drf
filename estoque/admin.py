from django.contrib import admin
from .models import Movimentacao, Produto


class MovimentacaoInline(admin.TabularInline):
    model = Movimentacao
    extra = 0
    readonly_fields = ("criado_em",)
    fields = ("tipo", "quantidade", "observacao", "criado_em")


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "preco",
        "get_saldo_estoque",
        "ativo",
        "criado_em",
    )
    list_filter = ("ativo", "criado_em", "atualizado_em")
    search_fields = ("nome", "descricao")
    readonly_fields = ("get_saldo_estoque", "criado_em", "atualizado_em")
    inlines = [MovimentacaoInline]

    @admin.display(description="Saldo em Estoque")
    def get_saldo_estoque(self, obj):
        return obj.saldo_estoque


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ("produto", "tipo", "quantidade", "criado_em")
    list_filter = ("tipo", "criado_em")
    search_fields = ("produto__nome", "observacao")
    readonly_fields = ("criado_em",)
    autocomplete_fields = ["produto"]
