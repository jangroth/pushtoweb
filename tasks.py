from invoke import task


@task
def update(ctx, what):
    """
    Update existing stack (web|code)
    """
    whats = ['web', 'code']
    if what not in whats:
        print('Allowed arguments: {}'.format(whats))
    else:
        ctx.run('bash scripts/update-{}-stack.sh')
