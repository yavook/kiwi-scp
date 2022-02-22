import logging

import click

from kiwi_scp.commands import KiwiCLI


@click.option(
    "-v", "--verbose",
    help="increase output verbosity",
    count=True,
)
@click.command(cls=KiwiCLI)
def main(verbose: int) -> None:
    """kiwi is the simple tool for managing container servers.

    \b
    - Manage full instances using just your favorite version control system
    - Group services into projects, each with their own docker-compose.yml
    - Build service-specific, private docker images from Dockerfiles
    - Make use of the local file system by referring to ${KIWI_PROJECT}, ${KIWI_INSTANCE} and ${KIWI_CONFIG} in compose files
    - Create your own instance-global variables for compose files using the kiwi.yml "environment" section
    """

    if verbose >= 2:
        log_level = logging.DEBUG
        log_format = "[%(asctime)s] %(levelname)s @ %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
    elif verbose >= 1:
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
