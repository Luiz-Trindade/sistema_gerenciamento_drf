# usuarios/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioRegistroSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet simplificado. Libera CRUD completo para admins em /usuarios/
    e cria rotas personalizadas (/me/ e /change_password/) para o usuário
    gerenciar o próprio perfil de forma segura.
    """

    queryset = Usuario.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioRegistroSerializer
        return UsuarioSerializer

    def get_permissions(self):
        # Apenas admins podem listar, recuperar, atualizar ou deletar outros usuários.
        if self.action in ["list", "destroy", "retrieve", "update", "partial_update"]:
            return [permissions.IsAdminUser()]

        # Qualquer usuário autenticado pode criar conta, acessar /me/ e /change_password/
        return [permissions.IsAuthenticated()]

    # ==========================================
    # Rota: /api/usuarios/me/
    # ==========================================
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

    # ==========================================
    # Rota: /api/usuarios/change_password/
    # ==========================================
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="change-password",  # Define a URL explicitamente como /change-password/
    )
    def change_password(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        # 1. Validação básica de campos obrigatórios
        if not current_password or not new_password:
            return Response(
                {"detail": "Senha atual e nova senha são obrigatórias."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Verifica se a senha atual fornecida está correta
        if not user.check_password(current_password):
            return Response(
                {"detail": "A senha atual está incorreta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Validação mínima de segurança da nova senha
        if len(new_password) < 6:
            return Response(
                {"detail": "A nova senha deve ter pelo menos 6 caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4. Define e salva a nova senha de forma segura (com hash)
        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK
        )
