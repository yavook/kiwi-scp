# system
import argparse


class Parser:
    """Singleton: Main CLI arguments parser"""

    class __Parser:
        """Singleton type"""

        # argparse objects
        __parser = None
        __subparsers = None
        __args = None

        def __init__(self):
            # create main parsers
            self.__parser = argparse.ArgumentParser(
                description='kiwi-config'
            )

            # main arguments
            self.__parser.add_argument(
                '-v', '--verbosity',
                action='count', default=0
            )

            # attach subparsers
            self.__subparsers = self.__parser.add_subparsers()
            self.__subparsers.required = True
            self.__subparsers.dest = 'command'

        def get_subparsers(self):
            return self.__subparsers

        def get_args(self):
            if self.__args is None:
                # parse args if needed
                self.__args = self.__parser.parse_args()

            return self.__args

    __instance = None

    def __init__(self):
        if Parser.__instance is None:
            # create singleton
            Parser.__instance = Parser.__Parser()

    def __getattr__(self, item):
        """Inner singleton direct access"""
        return getattr(self.__instance, item)
