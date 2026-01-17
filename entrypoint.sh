#!/usr/bin/env bash
set -euo pipefail

# Variables esperadas
host="${DB_HOST:-proyecto-db}"
port="${DB_PORT:-5432}"

echo "Esperando a la base de datos ${host}:${port}..."
until nc -z "$host" "$port"; do
  printf '.'
  sleep 1
done
echo "Base de datos disponible."

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput || true

if [ "${RESET_DB:-false}" = "true" ]; then
  echo "⚠️ Borrando base de datos (RESET_DB=true)"
  psql -U "$POSTGRES_USER" -d postgres <<EOF
DROP DATABASE IF EXISTS $POSTGRES_DB;
CREATE DATABASE $POSTGRES_DB;
EOF
fi


echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Iniciando servidor Gunicorn..."
exec gunicorn proyecto.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-level info

