import os
import sys
from enum import Enum, auto
from typing import List, Tuple, Iterable

import click

from ..instance import Instance


class KiwiCLI(click.MultiCommand):
    """Command Line Interface spread over multiple files in this directory"""

    def list_commands(self, ctx):
        """list all the commands defined by cmd_*.py files in this directory"""

        return (
            filename[4:-3]
            for filename in os.listdir(os.path.abspath(os.path.dirname(__file__)))
            if filename.startswith("cmd_") and filename.endswith(".py")
        )

    def get_command(self, ctx, name):
        """import and return a specific command"""

        try:
            mod = __import__(f"kiwi_scp.commands.cmd_{name}", None, None, ["CMD"])
        except ImportError:
            return
        return mod.CMD


class KiwiCommand:
    @staticmethod
    def print_multi_color(*content: Tuple[str, str]):
        for message, color in content:
            click.secho(message, fg=color, nl=False)
        click.echo()

    @staticmethod
    def print_header(header: str):
        click.secho(header, fg="green", bold=True)

    @staticmethod
    def print_error(header: str):
        click.secho(header, file=sys.stderr, fg="red", bold=True)

    @staticmethod
    def print_list(content: Iterable[str]):
        for item in content:
            KiwiCommand.print_multi_color(
                ("  - ", "green"),
                (item, "blue"),
            )

    @classmethod
    def run_for_instance(cls, instance: Instance, **kwargs) -> None:
        for project in instance.config.projects:
            cls.run_for_project(instance, project.name, **kwargs)

    @classmethod
    def run_for_project(cls, instance: Instance, project_name: str, **kwargs) -> None:
        project = instance.get_project(project_name)

        if project is None:
            click.secho(f"No project '{project_name}' in kiwi-scp instance at '{instance.directory}'.", fg="red", bold=True)
            return

        service_names = [service.name for service in project.get_services().content]

        cls.run_for_services(instance, project_name, service_names, **kwargs)

    @classmethod
    def run_for_services(cls, instance: Instance, project_name: str, service_names: List[str], **kwargs) -> None:
        pass


class KiwiCommandType(Enum):
    INSTANCE = auto()
    PROJECT = auto()
    SERVICE = auto()
