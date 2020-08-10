from ..config import LoadedConfig

from ._utils import SubCommand


class ShowCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'show',
            description="show effective kiwi.yml"
        )

    def run(self):
        config = LoadedConfig.get()
        print(config)
