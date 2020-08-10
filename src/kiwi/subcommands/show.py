from ..config import LoadedConfig
from ..core import Parser

from ._utils import SubCommand


class ShowCommand(SubCommand):
    command = 'show'

    @classmethod
    def setup(cls):
        parser = Parser.get_subparsers().add_parser(
            cls.command,
            description="Show effective kiwi.yml"
        )

    @classmethod
    def run(cls):
        config = LoadedConfig.get()
        print(config)
