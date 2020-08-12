from ..parser import Parser


class SubCommand:
    __name = None
    _sub_parser = None

    def __init__(self, name, **kwargs):
        self.__name = name
        self._sub_parser = Parser().get_subparsers().add_parser(name, **kwargs)

    def __str__(self):
        return self.__name

    def run(self, config, args):
        pass


