from rest_framework import viewsets
from .models import ContaReceber, Pedido
from .serializers import ContaReceberSerializer, PedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.prefetch_related(
        "movimentacoes", "contas_receber"
    ).select_related("usuario")
    serializer_class = PedidoSerializer

    def perform_create(self, serializer):
        # Associa automaticamente o usuário logado como responsável pelo pedido, se desejado
        serializer.save(usuario=self.request.user)


class ContaReceberViewSet(viewsets.ModelViewSet):
    queryset = ContaReceber.objects.select_related("pedido")
    serializer_class = ContaReceberSerializer
