from invoke import task
import os

@task
def configurar(c):
  c.run("pip install -r requirements.txt")

@task
def test(c):
  c.run("pytest app/test/test_perfiles.py")
  c.run("pytest app/test/test_suscripciones.py")

@task
def migrar(c):
  c.run("python manage.py makemigrations")
  c.run("python manage.py migrate")

@task
def resetear(c):
  if os.path.exists("db.sqlite3"):
    os.remove("db.sqlite3")

  migrations_path = os.path.join("app", "migrations")
  for archivo in os.listdir(migrations_path):
    if archivo.endswith("_initial.py"):
      os.remove(os.path.join(migrations_path, archivo))