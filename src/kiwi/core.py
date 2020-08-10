import argparse
import os

###########
# CONSTANTS

KIWI_ROOT = os.getenv('KIWI_ROOT', ".")
KIWI_CONF_NAME = os.getenv('KIWI_CONF_NAME', "kiwi.yml")


class Parser:
    class __Parser:
        __parser = None
        __subparsers = None
        __args = None

        def __init__(self):
            self.__parser = argparse.ArgumentParser(description='kiwi-config')

            self.__subparsers = self.__parser.add_subparsers()
            self.__subparsers.required = True
            self.__subparsers.dest = 'command'

        def get_parser(self):
            return self.__parser

        def get_subparsers(self):
            return self.__subparsers

        def get_args(self):
            if self.__args is None:
                self.__args = self.__parser.parse_args()

            return self.__args

    __instance = None

    def __init__(self):
        if Parser.__instance is None:
            Parser.__instance = Parser.__Parser()

    def __getattr__(self, item):
        return getattr(self.__instance, item)
