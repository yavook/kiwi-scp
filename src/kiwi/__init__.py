# local
from .parser import Parser
from .runner import Runner


def verbosity():
    _ = Runner()
    return Parser().get_args().verbosity


def run():
    Runner().run()


__all__ = [
    'verbosity',
    'run'
]
