# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .models import Usuario

# ==========================================
# 1. RESOURCE
# ==========================================


class UsuarioResource(resources.ModelResource):
    class Meta:
        model = Usuario
        fields = ("id", "email", "first_name", "last_name", "is_staff", "is_active")
        export_order = fields


# ==========================================
# 2. ADMIN
# ==========================================


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin, ModelAdmin, ImportExportModelAdmin):
    """
    Herdamos do ModelAdmin do Unfold, BaseUserAdmin do Django e ImportExportModelAdmin.
    """

    resource_classes = [UsuarioResource]
    import_form_class = ImportForm
    export_form_class = ExportForm

    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "is_staff", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["email", "first_name", "last_name"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Informações Pessoais"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissões"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Datas Importantes"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )
