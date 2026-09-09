from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin, ModelAdmin):
    """
    Herdamos do ModelAdmin do Unfold e do BaseUserAdmin do Django.
    Isso garante que a lógica de senhas do Django funcione com a UI do Unfold.
    """

    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "is_staff", "is_active"]
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
                    "password",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    # O Unfold as vezes requer que o filter_horizontal seja declarado explicitamente
    # para os campos ManyToMany do User (groups e permissions) renderizarem bonito
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
