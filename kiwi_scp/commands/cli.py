import importlib
import logging
import os
import sys
from enum import Enum, auto
from typing import List, Tuple, Iterable, Type, Optional, TypeVar

import click

from ..instance import Instance, Project, Services
from ..wstring import WParagraph, WAlignment

_logger = logging.getLogger(__name__)


class KiwiCLI(click.MultiCommand):
    """Command Line Interface spread over multiple files in this directory"""

    def list_commands(self, ctx: click.Context) -> List[str]:
        """list all the commands defined by cmd_*.py files in this directory"""

        return [
            filename[4:-3]
            for filename in os.listdir(os.path.abspath(os.path.dirname(__file__)))
            if filename.startswith("cmd_") and filename.endswith(".py")
        ]

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """import and return a specific command"""

        try:
            cmd_module = importlib.import_module(f"kiwi_scp.commands.cmd_{cmd_name}")

        except ImportError:
            return

        for cmd_name in dir(cmd_module):
            member = getattr(cmd_module, cmd_name)
            if isinstance(member, click.Command):
                return member


T = TypeVar("T")


class KiwiCommand:
    @staticmethod
    def print_multi_color(*content: Tuple[str, str]) -> None:
        for message, color in content:
            click.secho(message, fg=color, nl=False)
        click.echo()

    @staticmethod
    def print_header(header: str) -> None:
        click.secho(header, fg="green", bold=True)

    @staticmethod
    def print_error(error: str) -> None:
        click.secho(error, file=sys.stderr, fg="red", bold=True)

    @staticmethod
    def print_list(content: Iterable[str]) -> None:
        for item in content:
            KiwiCommand.print_multi_color(
                ("  - ", "green"),
                (item, "blue"),
            )

    @staticmethod
    def user_query(description: str, default: T, cast_to: Type[T] = str) -> T:
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

    @staticmethod
    def danger_confirm(*prompt_lines: str, default: Optional[bool] = None) -> bool:
        if default is True:
            suffix = "[YES|no]"
            default_answer = "yes"

        elif default is False:
            suffix = "[yes|NO]"
            default_answer = "no"

        else:
            suffix = "[yes|no]"
            default_answer = None

        dumb = WParagraph.from_strings(
            click.style("WARNING", bold=True, underline=True, blink=True, fg="red"),
            click.style("ここにゴミ", fg="cyan"),
            click.style("を捨てないで下さい", fg="cyan"),
            click.style("DO NOT DUMB HERE", fg="yellow"),
            click.style("NO DUMB AREA", fg="yellow"),
        ).align(WAlignment.CENTER).surround("!")

        prompt = WParagraph.from_strings(*prompt_lines).align(WAlignment.LEFT).emphasize(3)

        answer = input(
            f"{dumb}\n\n"
            f"{prompt}\n\n"
            f"Are you sure you want to proceed? {suffix}: "
        ).strip().lower()

        if not answer:
            answer = default_answer

        while answer not in ["yes", "no"]:
            answer = input("Please type 'yes' or 'no' explicitly: ").strip().lower()

        return answer == "yes"

    @classmethod
    def run(cls, instance: Instance, project_name: Optional[str] = None, service_names: Optional[List[str]] = None,
            **kwargs):

        _logger.debug(f"{instance.directory!r}: {project_name!r}, {service_names!r}")
        if project_name is None:
            # run for whole instance
            _logger.debug(f"running for instance, kwargs={kwargs}")
            cls.run_for_instance(instance, **kwargs)

        elif not service_names:
            # run for one entire project
            project = instance.get_project(project_name)
            if project is None:
                _logger.debug(f"running for new project {project_name}, kwargs={kwargs}")
                cls.run_for_new_project(instance, project_name, **kwargs)

            else:
                _logger.debug(f"running for project {project.name}, kwargs={kwargs}")
                cls.run_for_project(instance, project, **kwargs)

        else:
            # run for some services
            project = instance.get_project(project_name)
            if project is not None:
                _logger.debug(f"running for services {service_names} in project {project}, kwargs={kwargs}")
                cls.run_for_services(instance, project, service_names, **kwargs)

            else:
                cls.print_error(f"Project '{project_name}' not in kiwi-scp instance at '{instance.directory}'!")

    @classmethod
    def run_for_instance(cls, instance: Instance, **kwargs) -> None:
        for project_config in instance.config.projects:
            project = instance.get_project(project_config.name)
            cls.run_for_project(instance, project, **kwargs)

    @classmethod
    def run_for_project(cls, instance: Instance, project: Project, **kwargs) -> None:
        service_names = [service.name for service in project.services.content]
        cls.run_for_services(instance, project, service_names, **kwargs)

    @classmethod
    def run_for_new_project(cls, instance: Instance, project_name: str, **kwargs) -> None:
        cls.print_error(f"Project '{project_name}' not in kiwi-scp instance at '{instance.directory}'!")

    @classmethod
    def run_for_services(cls, instance: Instance, project: Project, service_names: List[str], **kwargs) -> None:
        services = project.services.filter_existing(service_names)

        new_service_names = [
            service_name
            for service_name
            in service_names
            if service_name not in list(services.names)
        ]

        cls.run_for_filtered_services(instance, project, services, new_service_names, **kwargs)

    @classmethod
    def run_for_filtered_services(cls, instance: Instance, project: Project, services: Services,
                                  new_service_names: List[str], **kwargs) -> None:
        raise Exception


class KiwiCommandType(Enum):
    INSTANCE = auto()
    PROJECT = auto()
    SERVICE = auto()
