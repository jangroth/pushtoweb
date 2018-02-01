from invoke import task


@task(optional=['web', 'code'])
def create(ctx, what):
    """
    Create stack (web|code)
    """
    print(what)
    # ctx.run('bash scripts/create-{}-stack.sh')


@task(optional=['web', 'code'])
def update(ctx, what):
    """
    Update stack (web|code)
    """
    ctx.run('bash scripts/update-{}-stack.sh'.format(what))


@task(optional=['web', 'code'])
def delete(ctx, what):
    """
    Delete stack (web|code)
    """
    ctx.run('bash scripts/delete-{}-stack.sh'.format(what))


@task(optional=['www', 'lambda'])
def upload(ctx, what):
    """
    Upload code (www|lambda)
    """
    ctx.run('bash scripts/upload-{}-stack.sh'.format(what))


@task
def run_in_docker(ctx):
    """
    Run lambda in local docker container
    """
    ctx.run('bash scripts/open-shell-into-local-lambda.sh')
