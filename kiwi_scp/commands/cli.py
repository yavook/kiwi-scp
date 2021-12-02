import importlib
import os
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

        for cmd_name in dir(cmd_module):
            member = getattr(cmd_module, cmd_name)
            if isinstance(member, click.Command):
                return member


