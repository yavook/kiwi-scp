# local
from .parser import Parser
from .runner import Runner


def verbosity():
    # ensure singleton is instantiated: runs subcommand setup routines
    _ = Runner()
    return Parser().get_args().verbosity


def run():
    # pass down
    return Runner().run()


__all__ = [
    'verbosity',
    'run'
]
