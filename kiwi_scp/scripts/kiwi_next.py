import click
import yaml

from kiwi_scp.commands.cli import KiwiCLI
from kiwi_scp.config import Config


@click.command(cls=KiwiCLI)
@click.pass_context
def main(ctx):
    """A complex command line interface."""

    with open("./kiwi.yml") as kc:
        yml = yaml.safe_load(kc)
        ctx.ensure_object(dict)
        ctx.obj["cfg"] = Config(**yml)

    click.echo("Hello main")


if __name__ == "__main__":
    main()
