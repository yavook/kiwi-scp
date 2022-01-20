import importlib
import os
from gettext import gettext as _
from typing import List, Optional

import click


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

        member_name = f"{cmd_name.capitalize()}Command"

        if member_name in dir(cmd_module):
            member = getattr(cmd_module, member_name)

            if isinstance(member, click.Command):
                return member

            else:
                raise Exception("Fail class")

        else:
            raise Exception("Fail member name")

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
            raise Exception(f"Some commands were not registered in a group above: {cmd_names}")
