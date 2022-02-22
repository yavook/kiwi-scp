import importlib
import os
from gettext import gettext as _
from typing import List, Optional

import click


class MissingCMDObjectError(ValueError):
    """raised if command object can't be found in its module"""
    pass


class CMDObjectSubclassError(TypeError):
    """raised if a command object is not inheriting click.Command"""
    pass


class CMDUnregisteredError(ValueError):
    """raised if commands have not been assigned to a command group"""

    unregistered: List[str]

    def __init__(self, unregistered):
        self.unregistered = unregistered

        super().__init__(f"Some commands were not registered in a group above: {unregistered!r}")


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

        cmd_object_name = f"{cmd_name.capitalize()}Command"

        if cmd_object_name in dir(cmd_module):
            cmd_object = getattr(cmd_module, cmd_object_name)

            if isinstance(cmd_object, click.Command):
                return cmd_object

            else:
                raise CMDObjectSubclassError()

        else:
            raise MissingCMDObjectError()

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        commands = {
            "Operation": [
                "up", "down", "restart", "update",
            ],
            "Instance Management": [
                "init", "list",
            ],
            "Project and Service Management": [
                "new", "enable", "disable", "logs", "shell", "cmd",
            ],
            "Image Handling": [
                "build", "pull", "push",
            ],
        }

        # allow for 3 times the default spacing
        cmd_names = set(self.list_commands(ctx))
        limit = formatter.width - 6 - max(len(cmd_name) for cmd_name in cmd_names)

        for purpose, cmd_list in commands.items():
            with formatter.section(_(f"Commands for {purpose}")):
                formatter.write_dl([
                    (cmd_name, self.get_command(ctx, cmd_name).get_short_help_str(limit))
                    for cmd_name in cmd_list
                ])

            cmd_names -= set(cmd_list)

        if len(cmd_names) > 0:
            raise CMDUnregisteredError(cmd_names)
