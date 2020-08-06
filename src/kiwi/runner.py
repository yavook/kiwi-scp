from typing import List

from .core import Parser
from .subcommands import *


class Runner:
    __commands: List[SubCommand] = [
        InitCommand
    ]

    @classmethod
    def setup_all(cls):
        for cmd in cls.__commands:
            cmd.setup()

    @classmethod
    def run(cls):
        args = Parser.get_args()

        for cmd in cls.__commands:
            if cmd.get_cmd() == args.command:
                cmd.run()
                return
