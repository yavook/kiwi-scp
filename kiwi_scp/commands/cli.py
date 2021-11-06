import os
import sys
from enum import Enum, auto
from typing import List, Tuple, Iterable, Any, Type

import click

from ..instance import Instance, Project, Services


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
    def print_error(error: str):
        click.secho(error, file=sys.stderr, fg="red", bold=True)

    @staticmethod
    def print_list(content: Iterable[str]):
        for item in content:
            KiwiCommand.print_multi_color(
                ("  - ", "green"),
                (item, "blue"),
            )

    @staticmethod
    def user_query(description: str, default: Any, cast_to: Type[Any] = str):
        # prompt user as per argument
        while True:
            try:
                prompt = \
                    click.style(f"Enter {description} [", fg="green") + \
                    click.style(default, fg="blue") + \
                    click.style("] ", fg="green")
                str_value = input(prompt).strip()
                if str_value:
                    return cast_to(str_value)
                else:
                    return default

            except EOFError:
                click.echo("Input aborted.")
                return default

            except Exception as e:
                click.echo(f"Invalid input: {e}")

    @classmethod
    def run_for_instance(cls, instance: Instance, **kwargs) -> None:
        for project_config in instance.config.projects:
            project = instance.get_project(project_config.name)
            cls.run_for_existing_project(instance, project, **kwargs)

    @classmethod
    def run_for_new_project(cls, instance: Instance, project_name: str, **kwargs) -> None:
        raise Exception

    @classmethod
    def run_for_existing_project(cls, instance: Instance, project: Project, **kwargs) -> None:
        service_names = [service.name for service in project.services.content]
        cls.run_for_services(instance, project, service_names, **kwargs)

    @classmethod
    def run_for_services(cls, instance: Instance, project: Project, service_names: List[str], **kwargs) -> None:
        raise Exception


class KiwiCommandType(Enum):
    INSTANCE = auto()
    PROJECT = auto()
    SERVICE = auto()
