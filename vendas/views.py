# vendas/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import ContaReceber
from .serializers import ContaReceberSerializer, PedidoSerializer
from .services import criar_pedido_com_itens
from .selectors import get_pedidos_detalhados, get_pedido_detalhado_por_id


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Pedidos de Venda.

    Usa selectors para otimizar queries (evita N+1) e services
    para centralizar regras de negócio complexas.
    """

    serializer_class = PedidoSerializer

    def get_queryset(self):
        """
        Retorna o queryset otimizado via selector.
        Usamos get_queryset() em vez de queryset direto para permitir
        futuras filtragens baseadas no request.user, se necessário.
        """
        return get_pedidos_detalhados()

    def get_object(self):
        """
        Sobrescreve get_object para usar o selector otimizado
        ao buscar um pedido específico pelo ID.
        """
        queryset = self.get_queryset()

        # Filtros padrão do DRF
        lookup_url_kwarg = self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        # Usa o selector com get() para manter a otimização
        obj = queryset.get(**filter_kwargs)

        # Verifica permissões (importante para segurança)
        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        """
        Cria um novo pedido com itens.

        A lógica de criação de movimentações de saída e validação
        de estoque está centralizada no service `criar_pedido_com_itens`.
        """
        # Copiamos os dados para não mutar o request.data original
        data = request.data.copy()

        # Extraímos os itens do payload. O formato esperado é uma lista.
        itens = data.pop("itens", [])

        if not itens:
            return Response(
                {
                    "itens": [
                        "É necessário fornecer pelo menos um item para criar o pedido."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Chama a regra de negócio unificada
            pedido = criar_pedido_com_itens(
                usuario=request.user,
                cliente_id=data.get("cliente"),
                status=data.get("status", "criado"),
                itens=itens,
            )

            # Serializa o pedido criado com o queryset otimizado
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"Erro interno ao processar pedido: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def perform_create(self, serializer):
        """
        Não fazemos nada aqui, pois o método `create` acima já lida
        com toda a lógica de salvamento via service.
        """
        pass


class ContaReceberViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Contas a Receber.
    """

    queryset = ContaReceber.objects.select_related("pedido").select_related(
        "pedido__cliente"
    )
    serializer_class = ContaReceberSerializer

    def get_queryset(self):
        """
        Retorna contas a receber com relacionamentos otimizados.
        Pode ser estendido para filtrar por usuário/cliente no futuro.
        """
        queryset = super().get_queryset()

        # Exemplo de filtro futuro:
        # if self.request.user.is_staff:
        #     return queryset
        # return queryset.filter(pedido__usuario=self.request.user)

        return queryset
