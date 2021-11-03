import logging
from typing import Callable, Type, Optional, Tuple

import click

from .cli import KiwiCommandType, KiwiCommand
from ..instance import Instance

_pass_instance = click.make_pass_decorator(
    Instance,
    ensure=True,
)

_project_arg = click.argument(
    "project",
    required=False,
    type=str,
)

_services_arg = click.argument(
    "services",
    metavar="[SERVICE]...",
    nargs=-1,
    type=str,
)

_logger = logging.getLogger(__name__)


def kiwi_command(
        name: str,
        command_type: KiwiCommandType,
        **decorator_kwargs,
) -> Callable:
    def decorator(command_cls: Type[KiwiCommand]) -> Callable:

        @click.command(
            name,
            help=command_cls.__doc__,
            **decorator_kwargs,
        )
        @_pass_instance
        def cmd(ctx: Instance, project: Optional[str] = None, services: Optional[Tuple[str]] = None,
                **kwargs) -> None:

            _logger.debug(f"{ctx.directory!r}: {project!r}, {services!r}")
            if project is None:
                # run for whole instance
                _logger.debug(f"running for instance, kwargs={kwargs}")
                command_cls.run_for_instance(ctx, **kwargs)

            elif not services:
                # run for one entire project
                _logger.debug(f"running for project {project}, kwargs={kwargs}")
                command_cls.run_for_project(ctx, project, **kwargs)

            else:
                # run for some services
                _logger.debug(f"running for services {services} in project {project}, kwargs={kwargs}")
                command_cls.run_for_services(ctx, project, list(services), **kwargs)

        if command_type is KiwiCommandType.PROJECT:
            cmd = _project_arg(cmd)

        elif command_type is KiwiCommandType.SERVICE:
            cmd = _project_arg(cmd)
            cmd = _services_arg(cmd)

        return cmd

    return decorator
