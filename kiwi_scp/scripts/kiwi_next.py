import click

from kiwi_scp.commands.cli import KiwiCLI


@click.command(cls=KiwiCLI)
def main():
    """kiwi is the simple tool for managing container servers."""


if __name__ == "__main__":
    main()
