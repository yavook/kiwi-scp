from typing import List

from .core import Parser
from .subcommands import *


class Runner:
    __commands: List[SubCommand] = [
        InitCommand,
        ShowCommand,
        LogsCommand
    ]

    @classmethod
    def setup_all(cls):
        for cmd in cls.__commands:
            cmd.setup()

    @classmethod
    def run(cls):
        args = Parser.get_args()

        for cmd in cls.__commands:
            if cmd.command == args.command:
                cmd.run()
                return
