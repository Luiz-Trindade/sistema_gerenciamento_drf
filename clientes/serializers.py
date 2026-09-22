from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            "id",
            "nome",
            "email",
            "telefone",
            "descricao",
            "cpf",
            "cnpj",
            "ativo",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]
        extra_kwargs = {
            "email": {"required": False, "allow_null": True, "allow_blank": True},
            "cpf": {"required": False, "allow_null": True, "allow_blank": True},
            "cnpj": {"required": False, "allow_null": True, "allow_blank": True},
            "telefone": {"required": False, "allow_null": True, "allow_blank": True},
            "descricao": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def validate_email(self, value):
        """Normaliza string vazia para None, evitando colisão de UNIQUE."""
        return value or None

    def validate_cpf(self, value):
        return value or None

    def validate_cnpj(self, value):
        return value or None
