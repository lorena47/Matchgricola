from invoke import task
import os
import shutil

EXCLUDED_DIRS = {"venv", ".venv", "env", ".env", "__pypackages__"}

@task
def configurar(c):
  c.run("pip install -r requirements.txt")

@task
def test(c):
  c.run("pytest test/test_models/test_HU1aHU3.py")
  c.run("pytest test/test_models/test_HU4aHU13.py")

@task
def migrar(c):
  c.run("python manage.py makemigrations base")
  c.run("python manage.py migrate base")

# @task
# def resetear(c):
#   if os.path.exists("db.sqlite3"):
#     os.remove("db.sqlite3")

#   for root, dirs, files in os.walk(".", topdown=True):
#     dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

#     for d in dirs:
#       full = os.path.join(root, d)

#       if d == "__pycache__":
#         shutil.rmtree(full)
#         print(f"Eliminado: {full}")
#         continue

#       if d == "migrations":
#         if os.path.exists(os.path.join(full, "__init__.py")):
#           shutil.rmtree(full)
#           print(f"Eliminado: {full}")

@task
def reconstruir(c):
  c.run("docker compose down -v")
  c.run("docker compose up --build")

@task
def levantar(c):
  c.run("docker compose up --build")

@task
def clustest(c):
  c.run("pytest --capture=no test/test_cluster/test_peticiones_cluster.py")

@task
def estaticos(c):
  c.run("python manage.py collestatic")

@task
def local(c):
  c.run("python manage.py runserver 8080")
