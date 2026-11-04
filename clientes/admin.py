# clientes/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .models import Cliente

# ==========================================
# 1. RESOURCE
# ==========================================


class ClienteResource(resources.ModelResource):
    class Meta:
        model = Cliente
        fields = (
            "id",
            "nome",
            "cpf",
            "cnpj",
            "telefone_1",
            "telefone_2",
            "telefone_3",
            "email_1",
            "email_2",
            "email_3",
            "ativo",
            "criado_em",
            "atualizado_em",
        )
        export_order = fields


# ==========================================
# 2. ADMIN
# ==========================================


@admin.register(Cliente)
class ClienteAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_classes = [ClienteResource]
    import_form_class = ImportForm
    export_form_class = ExportForm

    # Campos exibidos na tabela de listagem
    list_display = [
        "nome",
        "email_1",
        "telefone_1",
        "cpf",
        "cnpj",
        "ativo",
        "criado_em",
    ]

    # Campos que contêm link para abrir os detalhes/edição
    list_display_links = ["nome", "email_1"]

    # Edição rápida diretamente pela tabela
    list_editable = ["ativo"]

    # Barra lateral de filtros
    list_filter = ["ativo", "criado_em"]

    # Busca por texto (pesquisa nos múltiplos contatos e documentos)
    search_fields = [
        "nome",
        "cpf",
        "cnpj",
        "email_1",
        "email_2",
        "email_3",
        "telefone_1",
        "telefone_2",
        "telefone_3",
    ]

    # Campos que não podem ser editados manualmente
    readonly_fields = ["criado_em", "atualizado_em"]

    # Quantidade de itens por página
    list_per_page = 25

    # Organização visual dos campos no formulário de cadastro/edição
    fieldsets = (
        (
            "Informações Principais",
            {
                "fields": (
                    ("nome", "ativo"),
                    ("descricao",),
                ),
            },
        ),
        (
            "Telefones de Contato",
            {
                "fields": (("telefone_1", "telefone_2", "telefone_3"),),
            },
        ),
        (
            "E-mails de Contato",
            {
                "fields": (("email_1", "email_2", "email_3"),),
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
