import os
from enum import Enum, auto
from typing import List

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
            mod = __import__(f"kiwi_scp.commands.cmd_{name}", None, None, ["cmd"])
        except ImportError:
            return
        return mod.CMD


class KiwiCommand:
    @classmethod
    def run_for_instance(cls, instance: Instance, **kwargs):
        for project in instance.config.projects:
            cls.run_for_project(instance, project.name, **kwargs)

    @classmethod
    def run_for_project(cls, instance: Instance, project_name: str, **kwargs):
        service_names = [service.name for service in instance.get_services(project_name, None).content]
        cls.run_for_services(instance, project_name, service_names, **kwargs)

    @classmethod
    def run_for_services(cls, instance: Instance, project_name: str, services: List[str], **kwargs):
        pass


class KiwiCommandType(Enum):
    INSTANCE = auto()
    PROJECT = auto()
    SERVICE = auto()


