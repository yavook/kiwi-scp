from kiwi.config import Config
from kiwi.core import Parser

from .subcommand import SubCommand


class ShowCommand(SubCommand):
    __parser = None

    @classmethod
    def get_cmd(cls):
        return 'show'

    @classmethod
    def setup(cls):
        cls.__parser = Parser.get_subparsers().add_parser(cls.get_cmd(), help="Show effective kiwi.yml")

    @classmethod
    def run(cls):
        config = Config.load()
        print(config)
