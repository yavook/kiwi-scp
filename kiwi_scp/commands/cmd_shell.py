import logging
from typing import List, Optional

import click

from .cmd import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance
from ..project import Project
from ..services import Services

_logger = logging.getLogger(__name__)


@click.option(
    "-s", "--shell",
    help="shell to spawn",
    type=str,
)
@click.option(
    "-u", "--user",
    help="container user to run shell",
    type=str,
)
@kiwi_command(
    short_help="Spawn shell",
)
class ShellCommand(KiwiCommand):
    """Spawn shell inside a project's service"""

    type = KiwiCommandType.SERVICES
    enabled_only = True

    @classmethod
    def run_for_filtered_services(cls, instance: Instance, project: Project, services: Services,
                                  new_service_names: List[str], shell: Optional[str] = None,
                                  user: Optional[str] = None) -> None:
        # shells from KiwiConfig
        shells = [
            *(str(path) for path in instance.config.shells),
            # as a last resort, fall back to "/bin/sh" and "sh"
            "/bin/sh", "sh",
        ]

        # add shell from argument
        if shell is not None:
            shells.insert(0, shell)

        user_args = ["-u", user] if user is not None else []

        for service in services.content:
            try:
                use_shell = next(service.existing_executables(shells))
                _logger.debug(f"Using shell {use_shell!r}")

            except StopIteration:
                if shell is not None:
                    use_shell = shell
                    _logger.warning(
                        "Could not find a working shell in this container. "
                        f"Launching provided shell {use_shell!r} nevertheless. This might fail!"
                    )

                else:
                    _logger.warning(
                        f"Could not find any working shell among {shells!r} in this container. "
                        "Please suggest a shell using the '-s SHELL' command line option!"
                    )
                    continue

            # spawn shell
            COMPOSE_EXE.run(['exec', *user_args, service.name, use_shell], **project.process_kwargs)
