import os

import click


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
        return mod.cmd
