from invoke import task

@task
def configurar(c):
  c.run("pip install -r requirements.txt")