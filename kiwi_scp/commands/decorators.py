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
    metavar="PROJECT",
    required=False,  # TODO remove this line when PROJECTS logic is implemented
    type=str,
)

_projects_arg = click.argument(
    "project_names",
    metavar="[PROJECT]...",
    nargs=-1,
    type=str,
)

_services_arg_p = click.argument(
    "project_name",
    metavar="[PROJECT]",
    required=False,
    type=str,
)

_services_arg_s = click.argument(
    "service_names",
    metavar="[SERVICE]...",
    nargs=-1,
    type=str,
)


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
            if service_names is not None:
                service_names = list(service_names)

            command_cls.run(ctx, project_name, service_names, **kwargs)

        if cmd_type is KiwiCommandType.PROJECT:
            cmd = _project_arg(cmd)

        elif cmd_type is KiwiCommandType.PROJECTS:
            cmd = _projects_arg(cmd)

        elif cmd_type is KiwiCommandType.SERVICE:
            cmd = _services_arg_p(cmd)
            cmd = _services_arg_s(cmd)

        return cmd

    return decorator
