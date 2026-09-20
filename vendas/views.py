# vendas/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import ContaReceber
from .serializers import ContaReceberSerializer, PedidoSerializer
from .services import criar_pedido_com_itens
from .selectors import (
    get_pedidos_detalhados,
    get_pedido_detalhado_por_id,
)


class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer

    def get_queryset(self):
        return get_pedidos_detalhados()

    def get_object(self):
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = queryset.get(**filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        itens = data.pop("itens", [])

        # --- CORREÇÃO: Extrair dados de pagamento do payload ---
        pagar_agora = data.pop("pagar_agora", False)
        meio_pagamento = data.pop("meio_pagamento", None)

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
            pedido = criar_pedido_com_itens(
                usuario=request.user,
                cliente_id=data.get("cliente"),
                status=data.get("status", "criado"),
                itens=itens,
                pagar_agora=pagar_agora,  # <-- Passado para o service
                meio_pagamento=meio_pagamento,  # <-- Passado para o service
            )

            # Recarrega o pedido com as relações otimizadas
            pedido = get_pedido_detalhado_por_id(pedido.id)

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
        pass


class ContaReceberViewSet(viewsets.ModelViewSet):
    serializer_class = ContaReceberSerializer

    def get_queryset(self):
        from .selectors import get_contas_receber_detalhadas

        return get_contas_receber_detalhadas()

    def get_object(self):
        from .selectors import get_conta_receber_detalhada_por_id

        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = queryset.get(**filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
