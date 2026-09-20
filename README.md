<div align="center">

# Sistema de Gerenciamento Corporativo

### Trabalho Acadêmico — Big Data Python

**Faculdade FACI Wyden**

</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15+-red?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![uv](https://img.shields.io/badge/Package%20Manager-uv-black?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)

</div>

> Sistema de gerenciamento interno desenvolvido para otimizar fluxos operacionais, unificando controle de estoque, cadastro de clientes, emissão de pedidos de venda e gestão financeira de recebíveis em uma arquitetura modular de alta performance.

---

## 👥 Participantes

- **Caio Pantoja Correa** — 202302416071
- **Jessica Freire Carvalho** — 202404170527
- **Lohhana Lima Pinheiro** — 202508864207
- **Luiz Gabriel Magalhães Trindade** — 202302954812
- **Paulo Henrique Magno Moura** — 202302416081

**Orientadora:** Prof.ª Me. Larissa de Paula Serrão Garcia

---

## 🎓 Sobre o Projeto

Este projeto acadêmico apresenta uma solução full-stack modular para o gerenciamento corporativo. Aplica conceitos avançados de desenvolvimento web, APIs REST, persistência de dados relacionais, validação de regras de negócio e organização de sistemas em Python, servindo como base sólida para operações de vendas e controle financeiro.

## 📑 Sumário

- [Arquitetura do Backend](#-arquitetura-do-backend)
- [Módulos do Sistema (Apps)](#-módulos-do-sistema-apps)
- [Fluxo Operacional](#-fluxo-operacional)
- [Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [Como Executar](#-como-executar-o-projeto-localmente)
- [Documentação da API](#-documentação-da-api)
- [Licença](#-licença)

---

## 🏛️ Arquitetura do Backend

O projeto adota uma estrutura altamente modular baseada em **aplicações (apps)** do Django. Cada domínio de negócio é encapsulado de forma independente, seguindo o padrão de responsabilidades:

- **`models.py`**: Modelagem relacional via ORM, regras de negócio complexas, propriedades dinâmicas (`@property`), sinais (`signals`) e validações de integridade (`clean`).
- **`admin.py`**: Back-office customizado utilizando o **Django Unfold** (interface moderna baseada em Tailwind CSS, com paleta de cores customizada, ícones Material Symbols e navegação estruturada).
- **`serializers.py`**: Camada de tradução, desserialização e validação de payloads JSON para a API REST.
- **`views.py`**: Endpoints de API gerenciando o ciclo completo de requisições HTTP e permissões de acesso.

O diretório central **`core`** gerencia as configurações globais (`settings.py`), o roteador principal de URLs e otimizações de performance (como `django-cachalot` para cache de queries ORM).

---

## 📦 Módulos do Sistema (Apps)

- **`usuarios`:** Gestão customizada de usuários, perfis de acesso, autenticação JWT e permissões administrativas.
- **`clientes`:** Cadastro e gestão de clientes (Pessoa Física e Jurídica), com validação única de CPF/CNPJ, controle de status (ativo/inativo) e dados de contato, servindo como base obrigatória para a emissão de pedidos.
- **`estoque`:** Cadastro estruturado de produtos e registro de movimentações de entrada e saída, calculando de forma dinâmica e automática o saldo atual em estoque.
- **`vendas`:** Gestão completa do ciclo de pedidos. Vincula o cliente e o usuário responsável, agrupa movimentações de saída de estoque, calcula o valor total automaticamente e gerencia o módulo financeiro de **Contas a Receber** (suportando faturamento à vista ou parcelado, controle de vencimentos e baixas de pagamento).

---

## 🔄 Fluxo Operacional

1. **Cadastro Base:** O operador cadastra os **Produtos** (com preços) e os **Clientes** (PF ou PJ).
2. **Controle de Estoque:** As mercadorias entram no sistema por meio de movimentações de entrada, atualizando o saldo disponível.
3. **Emissão de Pedidos:** Uma venda é criada vinculando um **Cliente** e itens do estoque (movimentações de saída). O sistema calcula o valor total automaticamente.
4. **Gestão Financeira:** O pedido gera automaticamente as **Contas a Receber** (parcelas), permitindo o acompanhamento de status (Pendente, Pago, Cancelado), datas de vencimento e registro do meio de pagamento (Pix, boleto, cartão, etc.).

---

## 🛠️ Tecnologias Utilizadas

### Backend (API)

- **Linguagem:** Python 3.13
- **Framework:** Django & Django REST Framework (DRF)
- **Gerenciador de Pacotes:** `uv` (Astral)
- **Autenticação:** JWT (SimpleJWT)
- **Documentação:** OpenAPI 3 (drf-spectacular / Swagger / ReDoc)
- **Banco de Dados:** PostgreSQL (via Docker)
- **Admin:** Django Unfold (Tailwind CSS)

### Frontend (SPA)

- **Framework:** Vue.js 3 (Composition API)
- **UI Framework:** Quasar Framework
- **Estado e Roteamento:** Pinia & Vue Router

### Infraestrutura

- **Containers:** Docker & Docker Compose

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Gerenciador de pacotes e ambientes Python)
- Docker e Docker Compose

### Passos

1. **Clone o repositório:**

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd sistema_gerenciamento
    ```

2. **Crie e ative o ambiente virtual com `uv`:**

    ```bash
    uv venv
    # Linux / macOS
    source .venv/bin/activate
    # Windows
    .venv\Scripts\activate
    ```

3. **Instale as dependências:**

    ```bash
    uv pip install -r requirements.txt
    ```

4. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto baseado no `.env.example` (ajuste as credenciais do banco de dados se necessário).

5. **Inicie os serviços do Docker (Banco de Dados):**

    ```bash
    docker compose up -d db
    ```

6. **Execute as migrações e crie o superusuário:**

    ```bash
    uv run manage.py migrate
    uv run manage.py createsuperuser
    ```

7. **Inicie o servidor de desenvolvimento:**

    ```bash
    uv run manage.py runserver
    ```

8. **Iniciar em modo de produção:**
    ```bash
    uv run uvicorn core.asgi:application --host 0.0.0.0 --port 8000 --workers $(nproc)
    ```

---

## 📖 Documentação da API

Com o servidor rodando, a documentação interativa e esquematizada da API pode ser acessada através das rotas:

- **Swagger UI:** [http://localhost:8000/docs/](http://localhost:8000/docs/)
- **ReDoc:** [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

---

## 📄 Licença

Este projeto está licenciado sob a **GNU Affero General Public License v3.0 (AGPL-3.0)**.

<div align="center">

[![Licença GNU AGPL v3](https://www.gnu.org/graphics/agplv3-with-text-162x68.png)](https://www.gnu.org/licenses/agpl-3.0.html)

Consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes.

</div>
