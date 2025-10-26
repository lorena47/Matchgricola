from invoke import task

@task
def configurar(c):
  c.run("pip install -r requirements.txt")

@task
def test(c):
  c.run("pytest")

@task
def migrar(c):
  c.run("python manage.py makemigrations")
  c.run("python manage.py migrate")

@task
def resetear(c):
  c.run("rm db.sqlite3")
  c.run("rm app/migrations/*_initial.py")
