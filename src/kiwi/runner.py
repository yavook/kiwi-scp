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

        def run(self, command_name):
            for cmd in self.__commands:
                if str(cmd) == command_name:
                    cmd.run()
                    return True

            return False

    __instance = None

    def __init__(self):
        if Runner.__instance is None:
            Runner.__instance = Runner.__Runner()

    def __getattr__(self, item):
        return getattr(self.__instance, item)


if __name__ == 'kiwi.runner':
    _ = Runner()
