# local
from ._subcommand import SubCommand


class ShowCommand(SubCommand):
    """kiwi show"""

    def __init__(self):
        super().__init__(
            'show',
            description="Show effective kiwi.yml"
        )

    def run(self, config, args):
        print(config)
