from typing import Optional

from django.db.models import QuerySet
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
        return self.queryset.filter(nome__icontains=termo)

    def com_email(self) -> QuerySet:
        return self.queryset.filter(email__isnull=False)

    def sem_email(self) -> QuerySet:
        return self.queryset.filter(email__isnull=True)
