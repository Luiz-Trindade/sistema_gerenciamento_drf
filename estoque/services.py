from decimal import Decimal
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import Q, QuerySet, ProtectedError
from django.shortcuts import get_object_or_404

from .models import Produto

# ==========================================
# EXCEÇÕES DE DOMÍNIO
# ==========================================


class ProdutoServiceError(Exception):
    """Exceção base para erros da camada de serviço de Produto."""

    pass


class ProdutoEmUsoError(ProdutoServiceError):
    """Lançada ao tentar excluir um produto que possui movimentações no estoque."""

    pass


class ProdutoValidationError(ProdutoServiceError):
    """Lançada quando os dados do produto falham na validação."""

    pass


# ==========================================
# CLASSE DE SERVIÇO
# ==========================================


class ProdutoService:
    """
    Encapsula as regras de negócio e operações de persistência relativas aos Produtos.
    """

    @classmethod
    def listar(
        cls,
        termo_busca: Optional[str] = None,
        apenas_ativos: bool = False,
    ) -> QuerySet[Produto]:
        """
        Retorna a listagem de produtos com suporte a busca por nome/descrição e filtro por status.
        """
        queryset = Produto.objects.all()

        if apenas_ativos:
            queryset = queryset.filter(ativo=True)

        if termo_busca:
            termo = termo_busca.strip()
            queryset = queryset.filter(
                Q(nome__icontains=termo) | Q(descricao__icontains=termo)
            )

        return queryset

    @classmethod
    def obter_por_id(cls, produto_id: int) -> Produto:
        """
        Recupera uma instância de Produto pelo ID ou levanta Http404.
        """
        return get_object_or_404(Produto, pk=produto_id)

    @classmethod
    @transaction.atomic
    def criar(
        cls,
        dados: Dict[str, Any],
        imagem: Optional[UploadedFile] = None,
    ) -> Produto:
        """
        Instancia e persiste um novo produto no banco de dados.
        """
        produto = Produto(
            nome=dados.get("nome"),
            descricao=dados.get("descricao", ""),
            preco=dados.get("preco", Decimal("0.00")),
            ativo=dados.get("ativo", True),
            imagem=imagem,
        )

        try:
            produto.full_clean()
            produto.save()
            return produto
        except ValidationError as exc:
            raise ProdutoValidationError(exc.message_dict) from exc

    @classmethod
    @transaction.atomic
    def atualizar(
        cls,
        produto: Produto,
        dados: Dict[str, Any],
        imagem: Optional[UploadedFile] = None,
        remover_imagem: bool = False,
    ) -> Produto:
        """
        Atualiza os campos de um produto existente.
        """
        for campo in ["nome", "descricao", "preco", "ativo"]:
            if campo in dados:
                setattr(produto, campo, dados[campo])

        if remover_imagem and produto.imagem:
            produto.imagem.delete(save=False)
            produto.imagem = None
        elif imagem:
            produto.imagem = imagem

        try:
            produto.full_clean()
            produto.save()
            return produto
        except ValidationError as exc:
            raise ProdutoValidationError(exc.message_dict) from exc

    @classmethod
    @transaction.atomic
    def deletar(cls, produto: Produto) -> None:
        """
        Remove um produto do sistema.
        Lança ProdutoEmUsoError se houver chave estrangeira protegida (Movimentacao).
        """
        try:
            if produto.imagem:
                produto.imagem.delete(save=False)
            produto.delete()
        except ProtectedError as exc:
            raise ProdutoEmUsoError(
                f"O produto '{produto.nome}' não pode ser excluído pois possui movimentações associadas."
            ) from exc

    @classmethod
    @transaction.atomic
    def alternar_status(cls, produto: Produto) -> Produto:
        """
        Inverte a situação do campo `ativo` do produto.
        """
        produto.ativo = not produto.ativo
        produto.save(update_fields=["ativo", "atualizado_em"])
        return produto
