import logging

import click

from kiwi_scp.commands.cli import KiwiCLI


@click.command(cls=KiwiCLI)
def main() -> None:
    """kiwi is the simple tool for managing container servers."""

    verbosity = 0

    if verbosity >= 2:
        log_level = logging.DEBUG
        log_format = "[%(asctime)s] %(levelname)s @ %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
    elif verbosity >= 1:
        log_level = logging.INFO
        log_format = "[%(asctime)s] %(levelname)s: %(message)s"
    else:
        log_level = logging.WARNING
        log_format = "%(levelname)s: %(message)s"

    # add a new handler (needed to set the level)
    log_handler = logging.StreamHandler()
    logging.getLogger().addHandler(log_handler)

    logging.getLogger().setLevel(log_level)
    log_handler.setFormatter(logging.Formatter(log_format))


if __name__ == "__main__":
    main()
