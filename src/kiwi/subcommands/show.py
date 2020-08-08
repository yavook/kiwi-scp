from ..config import LoadedConfig
from ..core import Parser

from ._utils import SubCommand


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
        config = LoadedConfig.get()
        print(config)
