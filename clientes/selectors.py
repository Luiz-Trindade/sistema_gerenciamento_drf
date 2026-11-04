# clientes/selectors.py
from typing import Optional

from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from .models import Cliente


class BaseSelector:
    model = None

    def __init__(self, queryset: Optional[QuerySet] = None):
        if queryset is None:
            queryset = self.model.objects.all()
        self.queryset = queryset

    def all(self) -> QuerySet:
        return self.queryset

    def get(self, **kwargs):
        return get_object_or_404(self.queryset, **kwargs)

    def filter(self, **kwargs) -> QuerySet:
        return self.queryset.filter(**kwargs)


class ClienteSelector(BaseSelector):
    """Consultas relacionadas a Cliente."""

    model = Cliente

    def ativos(self) -> QuerySet:
        return self.queryset.filter(ativo=True)

    def inativos(self) -> QuerySet:
        return self.queryset.filter(ativo=False)

    def buscar(self, termo: str) -> QuerySet:
        return self.queryset.filter(
            Q(nome__icontains=termo)
            | Q(email_1__icontains=termo)
            | Q(email_2__icontains=termo)
            | Q(email_3__icontains=termo)
            | Q(telefone_1__icontains=termo)
            | Q(telefone_2__icontains=termo)
            | Q(telefone_3__icontains=termo)
            | Q(cpf__icontains=termo)
            | Q(cnpj__icontains=termo)
        )

    def com_email(self) -> QuerySet:
        return self.queryset.filter(
            Q(email_1__isnull=False)
            | Q(email_2__isnull=False)
            | Q(email_3__isnull=False)
        )

    def sem_email(self) -> QuerySet:
        return self.queryset.filter(
            email_1__isnull=True, email_2__isnull=True, email_3__isnull=True
        )
