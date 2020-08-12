# system
import logging

# local
from .config import LoadedConfig
from .parser import Parser
from .subcommands import *

###########
# CONSTANTS

SUBCOMMANDS = [
    InitCommand,
    ShowCommand,
    LogsCommand
]


class Runner:
    class __Runner:
        __commands = []

        def __init__(self):
            for cmd in SUBCOMMANDS:
                self.__commands.append(cmd())

        def run(self):
            config = LoadedConfig.get()
            args = Parser().get_args()

            for cmd in self.__commands:
                if str(cmd) == args.command:
                    logging.debug(f"Running '{cmd}' with args: {args}")
                    cmd.run(config, args)
                    return True

            return False

    __instance = None

    def __init__(self):
        if Runner.__instance is None:
            Runner.__instance = Runner.__Runner()

    def __getattr__(self, item):
        return getattr(self.__instance, item)
