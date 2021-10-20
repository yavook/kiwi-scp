import os

import click


class KiwiCLI(click.MultiCommand):
    def list_commands(self, ctx):
        result = []
        for filename in os.listdir(os.path.abspath(os.path.dirname(__file__))):
            if filename.startswith("cmd_") and filename.endswith(".py"):
                result.append(filename[4:-3])
        result.sort()
        return result

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"kiwi_scp.commands.cmd_{name}", None, None, ["cmd"])
        except ImportError:
            return
        return mod.cmd
