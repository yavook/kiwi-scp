# local
from ..subcommand import SubCommand
from ..config import LoadedConfig


class ShowCommand(SubCommand):
    """kiwi show"""

    def __init__(self):
        super().__init__(
            'show',
            action="Printing",
            description="Show effective kiwi.yml"
        )

    def _run_instance(self, runner, args):
        print(LoadedConfig.get())
        return True
