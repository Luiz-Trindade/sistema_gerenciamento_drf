from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    # Campos exibidos na tabela de listagem
    list_display = [
        "nome",
        "email",
        "telefone",
        "cpf",
        "cnpj",
        "ativo",
        "criado_em",
    ]

    # Campos que contêm link para abrir os detalhes/edição
    list_display_links = ["nome", "email"]

    # Edição rápida diretamente pela tabela
    list_editable = ["ativo"]

    # Barra lateral de filtros
    list_filter = ["ativo", "criado_em"]

    # Busca por texto (pesquisa em vários campos)
    search_fields = ["nome", "email", "cpf", "cnpj", "telefone"]

    # Campos que não podem ser editados manualmente
    readonly_fields = ["criado_em", "atualizado_em"]

    # Quantidade de itens por página
    list_per_page = 25

    # Organização visual dos campos no formulário de cadastro/edição
    fieldsets = (
        (
            "Informações Pessoais / Contato",
            {
                "fields": (
                    ("nome", "email"),
                    ("telefone", "ativo"),
                ),
            },
        ),
        (
            "Documentos",
            {
                "fields": (("cpf", "cnpj"),),
            },
        ),
        (
            "Datas de Registro",
            {
                "fields": (("criado_em", "atualizado_em"),),
                "classes": ("collapse",),
            },
        ),
    )
