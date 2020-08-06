import argparse
import os

###########
# CONSTANTS

KIWI_ROOT = os.getenv('KIWI_ROOT', ".")
KIWI_CONF_NAME = os.getenv('KIWI_CONF_NAME', "kiwi.yml")


class Parser:
    __instance = None
    __subparsers = None
    __args = None

    @classmethod
    def __init_instance(cls):
        if not cls.__instance:
            cls.__instance = argparse.ArgumentParser(description='kiwi-config')

            cls.__subparsers = Parser.__instance.add_subparsers()
            cls.__subparsers.required = True
            cls.__subparsers.dest = 'command'

    @classmethod
    def get_instance(cls):
        cls.__init_instance()
        return cls.__instance

    @classmethod
    def get_subparsers(cls):
        cls.__init_instance()
        return cls.__subparsers

    @classmethod
    def get_args(cls):
        if not cls.__args:
            cls.__args = cls.get_instance().parse_args()

        return cls.__args
