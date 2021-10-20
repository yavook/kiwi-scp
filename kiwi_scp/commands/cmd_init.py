import click

from ..config import Config


@click.command(
    "init",
    short_help="Initializes a repo."
)
@click.argument(
    "path",
    required=False,
    type=click.Path(resolve_path=True)
)
@click.pass_context
def cmd(ctx, path):
    """Initializes a repository."""
    kiwi: Config = ctx.obj["cfg"]
    click.echo("Hello init")
    click.echo(kiwi.kiwi_yml)
    pass
