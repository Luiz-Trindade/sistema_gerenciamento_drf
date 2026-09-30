from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .selectors import MovimentacaoSelector, ProdutoSelector
from .serializers import MovimentacaoSerializer, ProdutoSerializer
from .services import ProdutoEmUsoError, ProdutoService, ProdutoValidationError


class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        """Camada de Leitura: Manteve o ProdutoSelector para queries e filtros."""
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

    def perform_create(self, serializer):
        """Camada de Escrita: Delega a criação ao ProdutoService."""
        dados = serializer.validated_data
        imagem = self.request.FILES.get("imagem")

        try:
            serializer.instance = ProdutoService.criar(
                dados=dados,
                imagem=imagem,
            )
        except ProdutoValidationError as e:
            raise ValidationError(e.args[0])

    def perform_update(self, serializer):
        """Camada de Escrita: Delega a atualização ao ProdutoService."""
        produto = self.get_object()
        dados = serializer.validated_data
        imagem = self.request.FILES.get("imagem")
        remover_imagem = self.request.data.get("remover_imagem", False)

        try:
            serializer.instance = ProdutoService.atualizar(
                produto=produto,
                dados=dados,
                imagem=imagem,
                remover_imagem=remover_imagem,
            )
        except ProdutoValidationError as e:
            raise ValidationError(e.args[0])

    def destroy(self, request, *args, **kwargs):
        """Camada de Escrita: Captura a exclusão e trata erro de integridade de estoque."""
        produto = self.get_object()

        try:
            ProdutoService.deletar(produto)
            return Response(status=status.HTTP_24_NO_CONTENT)
        except ProdutoEmUsoError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
