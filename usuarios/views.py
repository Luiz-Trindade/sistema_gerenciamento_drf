from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioRegistroSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet simplificado. Libera CRUD completo para admins em /usuarios/
    e cria a rota /usuarios/me/ para o usuário ver/editar o próprio perfil.
    """

    queryset = Usuario.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioRegistroSerializer
        return UsuarioSerializer

    def get_permissions(self):
        # Apenas admins podem listar/deletar outros usuários.
        if self.action in ["list", "destroy", "retrieve", "update", "partial_update"]:
            return [permissions.IsAdminUser()]
        # Qualquer logado pode criar usuário (sua regra anterior) e acessar o /me/
        return [permissions.IsAuthenticated()]

    # Cria a rota extra /api/usuarios/me/
    @action(
        detail=False,
        methods=["get", "patch", "put"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        usuario = request.user

        if request.method == "GET":
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)

        elif request.method in ["PUT", "PATCH"]:
            partial = request.method == "PATCH"
            serializer = self.get_serializer(
                usuario, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
