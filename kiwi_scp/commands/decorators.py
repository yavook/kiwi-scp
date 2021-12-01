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
        **decorator_kwargs,
) -> Callable:
    def decorator(command_cls: Type[KiwiCommand]) -> Callable:

        @click.command(
            help=command_cls.__doc__,
            **decorator_kwargs,
        )
        @_pass_instance
        def cmd(ctx: Instance, project_name: Optional[str] = None, project_names: Optional[Tuple[str]] = None,
                service_names: Optional[Tuple[str]] = None, **kwargs) -> None:
            if command_cls.type is KiwiCommandType.INSTANCE:
                project_names = []

            elif command_cls.type is KiwiCommandType.PROJECTS:
                project_names = list(project_names)

            else:
                if project_name is None:
                    project_names = []

                else:
                    project_names = [project_name]

                if command_cls.type is KiwiCommandType.SERVICES:
                    service_names = list(service_names)

            command_cls.run(ctx, project_names, service_names, **kwargs)

        if command_cls.type is KiwiCommandType.PROJECT:
            cmd = _project_arg(cmd)

        elif command_cls.type is KiwiCommandType.PROJECTS:
            cmd = _projects_arg(cmd)

        elif command_cls.type is KiwiCommandType.SERVICES:
            cmd = _services_arg_p(cmd)
            cmd = _services_arg_s(cmd)

        return cmd

    return decorator
