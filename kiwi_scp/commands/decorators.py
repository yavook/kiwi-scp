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


def kiwi_command(
        name: str,
        command_type: KiwiCommandType,
        **kwargs,
) -> Callable:
    def decorator(command_cls: Type[KiwiCommand]) -> Callable:

        @click.command(name, **kwargs)
        @_pass_instance
        def cmd(ctx: Instance, project: Optional[str] = None, services: Optional[Tuple[str]] = None,
                **cmd_kwargs) -> None:
            print(f"{ctx.directory!r}: {project!r}, {services!r}")
            if project is None:
                # run for whole instance
                print(f"for instance: {cmd_kwargs}")
                command_cls.run_for_instance(ctx, **cmd_kwargs)

            elif not services:
                # run for one entire project
                print(f"for project {project}: {cmd_kwargs}")
                command_cls.run_for_project(ctx, project, **cmd_kwargs)

            else:
                # run for some services
                print(f"for services {project}.{services}: {cmd_kwargs}")
                command_cls.run_for_services(ctx, project, list(services), **cmd_kwargs)

        if command_type is KiwiCommandType.PROJECT:
            cmd = _project_arg(cmd)

        elif command_type is KiwiCommandType.SERVICE:
            cmd = _project_arg(cmd)
            cmd = _services_arg(cmd)

        return cmd

    return decorator