from invoke import task


@task
def hello(ctx):
    print('hello world')
