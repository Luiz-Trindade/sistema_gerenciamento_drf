from rest_framework import viewsets

from .models import Movimentacao, Produto
from .serializers import MovimentacaoSerializer, ProdutoSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer


class MovimentacaoViewSet(viewsets.ModelViewSet):
    queryset = Movimentacao.objects.select_related("produto")
    serializer_class = MovimentacaoSerializer
