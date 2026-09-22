from rest_framework import viewsets

from .selectors import MovimentacaoSelector, ProdutoSelector
from .serializers import MovimentacaoSerializer, ProdutoSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        selector = ProdutoSelector()
        queryset = selector.all()

        ativo = self.request.query_params.get("ativo")
        if ativo is not None:
            if ativo.lower() in ("1", "true", "sim"):
                queryset = ProdutoSelector(queryset).ativos()
            else:
                queryset = ProdutoSelector(queryset).inativos()

        search = self.request.query_params.get("search")
        if search:
            queryset = ProdutoSelector(queryset).buscar(search)

        return queryset


class MovimentacaoViewSet(viewsets.ModelViewSet):
    serializer_class = MovimentacaoSerializer

    def get_queryset(self):
        selector = MovimentacaoSelector()
        queryset = selector.all()

        produto_id = self.request.query_params.get("produto")
        if produto_id:
            queryset = MovimentacaoSelector(queryset).por_produto_id(produto_id)

        tipo = self.request.query_params.get("tipo")
        if tipo:
            queryset = MovimentacaoSelector(queryset).por_tipo(tipo)

        return queryset
