FROM python:3.13-slim

# Agrupa ENV e desativa cache/verificações do pip via variável de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Se precisar de pacotes que compilam C (ex: Pillow, psycopg2), 
# instale as deps do sistema e apague o cache no mesmo RUN:
# RUN apt-get update && apt-get install -y --no-install-recommends gcc \
#     && rm -rf /var/lib/apt/lists/*

# Instala dependências (aproveita o cache do Docker)
COPY pyproject.toml .
RUN pip install .

# Copia o código
COPY . .

# Uvicorn
# CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && uvicorn core.asgi:application --host 0.0.0.0 --port 8000 --workers $(nproc)"]

# Granian
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && granian --interface asgi core.asgi:application --host 0.0.0.0 --port 8000 --workers $(nproc)"]
