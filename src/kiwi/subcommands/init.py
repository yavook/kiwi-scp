import logging
import os

from kiwi.core import KIWI_CONF_NAME, Parser
from kiwi.config import Config

from .subcommand import SubCommand


def user_input(config, key, prompt):
    # prompt user as per argument
    result = input("{} [Default: {}] ".format(prompt, config[key])).strip()

    # store result if present
    if result:
        config[key] = result


class InitCommand(SubCommand):
    __parser = None

    @classmethod
    def get_cmd(cls):
        return 'init'

    @classmethod
    def setup(cls):
        cls.__parser = Parser.get_subparsers().add_parser(cls.get_cmd(), help="Create new kiwi-config instance")
        # cls.__parser.add_argument('cmd', metavar='command', type=str, help='subcommand to execute')

    @classmethod
    def run(cls):
        config = Config.default()

        if os.path.isfile(KIWI_CONF_NAME):
            logging.warning("Overwriting existing '%s'!", KIWI_CONF_NAME)

        user_input(config, 'version', "Choose kiwi-config version")

        user_input(config, 'markers:project', "Enter marker string for project directories")
        user_input(config, 'markers:down', "Enter marker string for disabled projects")

        user_input(config, 'network:name', "Enter name for local docker network")
        user_input(config, 'network:cidr', "Enter CIDR block for local docker network")

        user_input(config, 'runtime:storage', "Enter main directory for local data")

        config.save()
