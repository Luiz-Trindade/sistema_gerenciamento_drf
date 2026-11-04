# clientes/serializers.py
from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            "id",
            "nome",
            "cpf",
            "cnpj",
            "descricao",
            "telefone_1",
            "telefone_2",
            "telefone_3",
            "email_1",
            "email_2",
            "email_3",
            "ativo",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]
        extra_kwargs = {
            "cpf": {"required": False, "allow_null": True, "allow_blank": True},
            "cnpj": {"required": False, "allow_null": True, "allow_blank": True},
            "descricao": {"required": False, "allow_null": True, "allow_blank": True},
            "telefone_1": {"required": False, "allow_null": True, "allow_blank": True},
            "telefone_2": {"required": False, "allow_null": True, "allow_blank": True},
            "telefone_3": {"required": False, "allow_null": True, "allow_blank": True},
            "email_1": {"required": False, "allow_null": True, "allow_blank": True},
            "email_2": {"required": False, "allow_null": True, "allow_blank": True},
            "email_3": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def validate_cpf(self, value):
        """Normaliza string vazia para None, evitando colisão de UNIQUE."""
        return value or None

    def validate_cnpj(self, value):
        return value or None
