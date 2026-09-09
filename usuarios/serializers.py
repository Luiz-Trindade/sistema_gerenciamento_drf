from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "email", "first_name", "last_name", "is_active", "date_joined"]
        read_only_fields = ["id", "email", "is_active", "date_joined"]


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = Usuario
        fields = ["id", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)
