import typing as t
from typing import Tuple

import click

from .cli import pass_instance
from ..config import ProjectConfig
from ..instance import Instance, Services
from ..misc import service_command


class KiwiCommand:
    @classmethod
    def run_for_instance(cls, instance: Instance, **kwargs):
        for project in instance.config.projects:
            cls.run_for_project(instance, project, **kwargs)

    @classmethod
    def run_for_project(cls, instance: Instance, project: ProjectConfig, **kwargs):
        cls.run_for_services(instance, project, instance.get_services(project.name, None), **kwargs)

    @classmethod
    def run_for_services(cls, instance: Instance, project: ProjectConfig, services: Services, **kwargs):
        pass


def kiwi_command(
        name: str,
        **kwargs,
) -> t.Callable:
    def decorator(command_cls: t.Type[KiwiCommand]) -> t.Callable:

        @click.command(name, **kwargs)
        @pass_instance
        @service_command
        def cmd(ctx: Instance, project: t.Optional[str], services: Tuple[str], **cmd_kwargs) -> None:
            print(f"{ctx.directory!r}: {project!r}, {services!r}")
            if project is None:
                # run for whole instance
                print("instance")
                command_cls.run_for_instance(ctx, **cmd_kwargs)

            elif not services:
                # run for one entire project
                print("project")
                for project_cfg in ctx.config.projects:
                    if project_cfg.name == project:
                        command_cls.run_for_project(ctx, project_cfg, **kwargs)

            else:
                # run for some services
                print("services")
                for project_cfg in ctx.config.projects:
                    if project_cfg.name == project:
                        services = ctx.get_services(project_cfg.name, services)
                        command_cls.run_for_services(ctx, project_cfg, services)

        return cmd

    return decorator


@kiwi_command(
    "list",
    short_help="Inspect a kiwi-scp instance",
)
class cmd(KiwiCommand):
    @classmethod
    def run_for_instance(cls, instance: Instance, **kwargs):
        print(instance.config.projects)

    @classmethod
    def run_for_services(cls, instance: Instance, project: ProjectConfig, services: Services, **kwargs):
        print(services)


# @click.command(
#     "list",
#     short_help="Inspect a kiwi-scp instance",
# )
# @pass_instance
# @service_command
# def cmd(ctx: Instance, project: str, services: Tuple[str]):
#     """List projects in this instance, services inside a project or service(s) inside a project"""
#     print(f"project: {project!r}, services: {services!r}")
#     if project is not None:
#         print(ctx.get_services(project, services))
#     else:
#         print(f"projects: {ctx.config.projects}")
