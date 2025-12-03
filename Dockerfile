FROM python:3.11-slim

# No escribir .pyc y usar buffering de stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema necesarias para compilación y netcat para esperar DB
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

# Copiar fichero de requerimientos e instalar
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copiar el resto de la app
COPY . /app

# Copiar entrypoint y hacerlo ejecutable
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

# Ejecutar entrypoint (lanza migraciones y comienza gunicorn)
CMD ["entrypoint.sh"]
