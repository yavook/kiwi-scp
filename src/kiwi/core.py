import argparse
import os

###########
# CONSTANTS

KIWI_ROOT = os.getenv('KIWI_ROOT', ".")
KIWI_CONF_NAME = os.getenv('KIWI_CONF_NAME', "kiwi.yml")


class Parser:
    __parser = None
    __subparsers = None
    __args = None

    @classmethod
    def get_parser(cls):
        if cls.__parser is None:
            cls.__parser = argparse.ArgumentParser(description='kiwi-config')

            cls.__parser.add_argument(
                '-v', '--verbose',
                action='count', default=0
            )

        return cls.__parser

    @classmethod
    def get_subparsers(cls):
        if cls.__subparsers is None:
            cls.__subparsers = cls.get_parser().add_subparsers()
            cls.__subparsers.required = True
            cls.__subparsers.dest = 'command'

        return cls.__subparsers

    @classmethod
    def get_args(cls):
        if cls.__args is None:
            cls.__args = cls.get_parser().parse_args()

        return cls.__args

