# clientes/models.py
from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="E-mail")
    telefone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Telefone"
    )
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    cpf = models.CharField(
        max_length=14, unique=True, blank=True, null=True, verbose_name="CPF"
    )
    cnpj = models.CharField(
        max_length=18, unique=True, blank=True, null=True, verbose_name="CNPJ"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["-criado_em"]

    def __str__(self):
        return self.nome
