<div align="center">

# Sistema de Gerenciamento

### Trabalho acadêmico — Big Data Python

**Faculdade FACI Wyden**

</div>

Sistema de gerenciamento interno corporativo desenvolvido para otimizar fluxos operacionais, unificando controle de estoque, emissão de pedidos de venda, auditoria de usuários e gestão financeira de recebíveis em uma arquitetura modular de alta performance.

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)

> Projeto desenvolvido para a disciplina **Big Data Python**, do curso da **Faculdade FACI Wyden**.

---

## 👥 Participantes

- Caio Pantoja Correa — 202302416071
- Jessica Freire Carvalho — 202404170527
- Lohhana Lima Pinheiro — 202508864207
- Luiz Gabriel Magalhães Trindade — 202302954812
- Paulo Henrique Magno Moura — 202302416081

**Orientadora:** Prof.ª Me. Larissa de Paula Serrão Garcia

## 🎓 Sobre o projeto

Este projeto acadêmico apresenta uma solução modular para o gerenciamento corporativo de estoque, vendas, usuários e contas a receber, aplicando conceitos de desenvolvimento web, APIs REST, persistência de dados e organização de sistemas em Python.

## 📑 Sumário

- [Arquitetura do Backend](#-arquitetura-do-backend)
- [Módulos do Sistema](#-módulos-do-sistema-apps)
- [Fluxo Operacional](#-fluxo-operacional)
- [Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [Como Executar](#-como-executar-o-backend-localmente)
- [Documentação da API](#-documentação-da-api)
- [Licença](#-licença)

---

## 🏛️ Arquitetura do Backend

O projeto adota uma estrutura altamente modular baseada em **aplicações (apps)** do Django. Cada domínio de negócios é encapsulado de forma independente, replicando o seguinte padrão de responsabilidades:

- **`models.py`**: Modelagem relacional via ORM, regras de negócio complexas, propriedades dinâmicas e validações de integridade.
- **`admin.py`**: Back-office customizado utilizando o **Django Unfold** (interface moderna baseada em Tailwind CSS, paleta azul customizada, desativação global de bordas arredondadas, ícones via Material Symbols e navegação estruturada).
- **`serializers.py`**: Camada de tradução, desserialização e validação de payloads JSON para a API REST.
- **`views.py`**: Endpoints de API gerenciando o ciclo completo de requisições HTTP (`GET`, `POST`, `PATCH`, `DELETE`).

O diretório central **`core`** centraliza as configurações globais do sistema (`settings.py`), o roteador principal de URLs (`urls.py`) e otimizações de performance em disco utilizando **`django-cachalot`** com backend baseado em arquivos.

---

## 📦 Módulos do Sistema (Apps)

- **`usuarios`:** Gestão customizada de usuários do sistema, perfis de acesso, senhas e permissões administrativas.
- **`estoque`:** Cadastro estruturado de produtos (com validação de preços e status) e registro de movimentações de entrada e saída, calculando de forma dinâmica e automática o saldo atual em estoque.
- **`vendas`:** Gestão completa do ciclo de pedidos de venda integrados às movimentações de saída de estoque. Calcula automaticamente o valor total do pedido com base nos itens e preços vigentes, vincula o usuário responsável para fins de auditoria e gerencia o módulo financeiro de **Contas a Receber** (suportando faturamento à vista ou parcelado, controle de parcelas, meios de pagamento, datas de vencimento e baixas de recebimento).

---

## 🔄 Fluxo Operacional

1. **Cadastro de Produtos:** O operador cadastra os itens definindo nome, descrição detalhada e preço unitário.
2. **Controle de Estoque:** As mercadorias entram ou saem por meio de movimentações, atualizando o saldo disponível dinamicamente.
3. **Emissão de Pedidos de Venda:** A venda agrupa as movimentações de saída de estoque de forma exclusiva, calculando o valor total do pedido automaticamente.
4. **Gestão Financeira (Contas a Receber):** O pedido gera parcelas financeiras permitindo o acompanhamento de recebimentos, status operacionais, datas de vencimento e meios de pagamento (Pix, boleto, cartão, etc.).

---

## 🛠️ Tecnologias Utilizadas

### Backend (API)

- **Linguagem:** Python 3.13
- **Framework:** Django & Django REST Framework (DRF)
- **Autenticação:** JWT (SimpleJWT)
- **Documentação:** OpenAPI 3 (drf-spectacular / Swagger / ReDoc)
- **Banco de Dados e cache:** PostgreSQL (via Docker) + `django-cachalot` (cache baseado em arquivos em `.django_cache/`)
- **Admin:** Django Admin customizado com **Django Unfold** (Tailwind CSS)

### Frontend (SPA)

- **Framework:** Vue.js 3 (Composition API)
- **UI Framework:** Quasar Framework
- **Estado e Roteamento:** Pinia & Vue Router

### Infraestrutura

- **Containers:** Docker & Docker Compose

---

## 🚀 Como Executar o Backend Localmente

### Pré-requisitos

- Python 3.13+
- Docker e Docker Compose (para o banco de dados)

### Passos

1. **Clone o repositório:**

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd sistema_gerenciamento_drf

```

2. **Crie e ative o ambiente virtual:**

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt

```

4. **Inicie os serviços do Docker (Banco de Dados):**

```bash
docker compose up -d db

```

5. **Execute as migrações e crie o superusuário:**

```bash
python manage.py migrate
python manage.py createsuperuser

```

6. **Inicie o servidor de desenvolvimento:**

```bash
python manage.py runserver

```

---

## 📖 Documentação da API

Com o servidor rodando, a documentação interativa da API pode ser acessada através das rotas:

- **Swagger UI:** [localhost:8000/docs](http://localhost:8000/docs/)
- **ReDoc:** [localhost:8000/redoc](http://localhost:8000/redoc/)

---

## 📄 Licença

Este projeto está licenciado sob a **GNU Affero General Public License v3.0 (AGPL-3.0)**.

<div align="center">

[![Licença GNU AGPL v3](https://www.gnu.org/graphics/agplv3-with-text-162x68.png)](https://www.gnu.org/licenses/agpl-3.0.html)

Consulte o arquivo [`LICENSE`](LICENSE) ou a [versão oficial da licença no site do GNU](https://www.gnu.org/licenses/agpl-3.0.html) para mais detalhes.

</div>
