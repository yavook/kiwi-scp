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
    "project_name",
    metavar="[PROJECT]",
    required=False,
    type=str,
)

_services_arg = click.argument(
    "service_names",
    metavar="[SERVICE]...",
    nargs=-1,
    type=str,
)

_logger = logging.getLogger(__name__)


def kiwi_command(
        cmd_type: KiwiCommandType = KiwiCommandType.SERVICE,
        **decorator_kwargs,
) -> Callable:
    def decorator(command_cls: Type[KiwiCommand]) -> Callable:

        @click.command(
            help=command_cls.__doc__,
            **decorator_kwargs,
        )
        @_pass_instance
        def cmd(ctx: Instance, project_name: Optional[str] = None, service_names: Optional[Tuple[str]] = None,
                **kwargs) -> None:

            _logger.debug(f"{ctx.directory!r}: {project_name!r}, {service_names!r}")
            if project_name is None:
                # run for whole instance
                _logger.debug(f"running for instance, kwargs={kwargs}")
                command_cls.run_for_instance(ctx, **kwargs)

            elif not service_names:
                # run for one entire project
                project = ctx.get_project(project_name)
                if project is not None:
                    _logger.debug(f"running for existing project {project}, kwargs={kwargs}")
                    command_cls.run_for_project(ctx, project, **kwargs)

                else:
                    _logger.debug(f"running for new project {project_name}, kwargs={kwargs}")
                    command_cls.run_for_new_project(ctx, project_name, **kwargs)

            else:
                # run for some services
                project = ctx.get_project(project_name)
                if project is not None:
                    _logger.debug(f"running for services {service_names} in project {project}, kwargs={kwargs}")
                    command_cls.run_for_services(ctx, project, list(service_names), **kwargs)

                else:
                    KiwiCommand.print_error(f"Project '{project_name}' not in kiwi-scp instance at '{ctx.directory}'!")

        if cmd_type is KiwiCommandType.PROJECT:
            cmd = _project_arg(cmd)

        elif cmd_type is KiwiCommandType.SERVICE:
            cmd = _project_arg(cmd)
            cmd = _services_arg(cmd)

        return cmd

    return decorator
