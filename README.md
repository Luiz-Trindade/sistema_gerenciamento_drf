# Sistema de Gerenciamento

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.x-red.svg)](https://www.django-rest-framework.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Quasar](https://img.shields.io/badge/Quasar-2.x-1976D2.svg?logo=quasar&logoColor=white)](https://quasar.dev/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Sistema de gerenciamento interno desenvolvido especificamente para atender às regras de negócio e fluxos operacionais da empresa.

O projeto é dividido em um Backend robusto servindo uma API REST e um Frontend responsivo e interativo.

---

## 🛠️ Tecnologias Utilizadas

### Backend (API)

- **Linguagem:** Python 3
- **Framework:** Django & Django REST Framework (DRF)
- **Autenticação:** JWT (SimpleJWT)
- **Documentação:** OpenAPI 3 (drf-spectacular / Swagger / ReDoc)
- **Banco de Dados:** PostgreSQL (via Docker)
- **Admin:** Django Admin customizado com Jazzmin

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

- **Swagger UI:** [http://localhost:8000/docs/](http://localhost:8000/docs/)
- **ReDoc:** [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

---

## 📄 Licença

Este projeto está licenciado sob a licença **GNU Affero General Public License v3.0 (AGPL-3.0)**.
Veja o arquivo [LICENSE](https://www.google.com/search?q=LICENSE) para mais detalhes.
