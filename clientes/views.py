from rest_framework import filters, viewsets
from .models import Cliente
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para realizar CRUD completo da entidade Cliente."""

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # Busca textual nativa (ex: ?search=joao)
    search_fields = ["nome", "email", "cpf", "cnpj", "telefone"]

    # Ordenação nativa (ex: ?ordering=nome ou ?ordering=-criado_em)
    ordering_fields = ["nome", "criado_em"]
    ordering = ["-criado_em"]
