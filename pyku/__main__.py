import click


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    '-c',
    '--channel',
    help='Path to channel project\'s root dir',
    required=True
)
def deploy():
    click.echo('deploy')


if __name__ == '__main__':
    cli()
