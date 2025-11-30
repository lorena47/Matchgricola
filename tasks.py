from invoke import task
import os
import shutil

EXCLUDED_DIRS = {"venv", ".venv", "env", ".env", "__pypackages__"}

@task
def configurar(c):
  c.run("pip install -r requirements.txt")

@task
def test(c):
  c.run("pytest app/test/test_models/test_HU1aHU3.py")
  c.run("pytest app/test/test_models/test_HU4aHU13.py")

@task
def migrar(c):
  c.run("python manage.py makemigrations")
  c.run("python manage.py migrate")

@task
def resetear(c):
  if os.path.exists("db.sqlite3"):
    os.remove("db.sqlite3")

  for root, dirs, files in os.walk(".", topdown=True):
    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

    for d in dirs:
      full = os.path.join(root, d)

      if d == "__pycache__":
        shutil.rmtree(full)
        print(f"Eliminado: {full}")
        continue

      if d == "migrations":
        if os.path.exists(os.path.join(full, "__init__.py")):
          shutil.rmtree(full)
          print(f"Eliminado: {full}")