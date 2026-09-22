from rest_framework import filters, viewsets

from .selectors import ClienteSelector
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para realizar CRUD completo da entidade Cliente."""

    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nome", "email", "cpf", "cnpj", "telefone"]
    ordering_fields = ["nome", "criado_em"]
    ordering = ["-criado_em"]

    def get_queryset(self):
        return ClienteSelector().all()