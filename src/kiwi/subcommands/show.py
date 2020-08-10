from ..config import LoadedConfig
from ..core import Parser

from ._utils import SubCommand


class ShowCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'logs',
            description="Show logs of a project"
        )

    def run(self):
        config = LoadedConfig.get()
        print(config)
