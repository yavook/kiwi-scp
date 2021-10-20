import click

from kiwi_scp.commands.cli import KiwiCLI


@click.command(cls=KiwiCLI)
def main():
    """main entry point for command line interface"""

    click.echo("Hello main")
    pass


if __name__ == "__main__":
    main()
