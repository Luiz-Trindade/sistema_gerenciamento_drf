# clientes/views.py
from rest_framework import filters, viewsets

from .selectors import ClienteSelector
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para realizar CRUD completo da entidade Cliente."""

    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
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
    ordering_fields = ["nome", "criado_em"]
    ordering = ["-criado_em"]

    def get_queryset(self):
        return ClienteSelector().all()
