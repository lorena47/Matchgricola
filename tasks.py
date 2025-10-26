from invoke import task

@task
def configurar(c):
  c.run("pip install -r requirements.txt")

@task
def test(c):
  c.run("pytest")