import click

from .cli import KiwiCTX, pass_kiwi_ctx


@click.command(
    "init",
    short_help="Initializes kiwi-scp"
)
@click.argument(
    "path",
    required=False,
    type=click.Path(resolve_path=True)
)
@pass_kiwi_ctx
def cmd(ctx: KiwiCTX, path):
    """Initialize or reconfigure a kiwi-scp instance"""

    click.echo(f"Hello init, kiwi version {ctx.config.version}")
    pass
