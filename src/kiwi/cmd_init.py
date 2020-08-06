import logging
import os

from .core import KIWI_CONF_NAME, Parser, SubCommand
from .config import Config


class InitSubCommand(SubCommand):
    def __init__(self):
        super(InitSubCommand, self).__init__('init')

    def setup(self):
        init_parser = Parser.get_subparsers().add_parser(str(self), help="Create new kiwi-config instance")
        # init_parser.add_argument('cmd', metavar='command', type=str, help='subcommand to execute')

    def __user_input(self, config, key, prompt):
        # prompt user as per argument
        result = input("{} [Current: {}] ".format(prompt, config[key])).strip()

        # store result if present
        if result:
            config[key] = result

    def run(self):
        config = Config.default()

        if os.path.isfile(KIWI_CONF_NAME):
            logging.warning("Overwriting existing '%s'!", KIWI_CONF_NAME)

        self.__user_input(config, 'version', "Choose kiwi-config version")

        self.__user_input(config, 'markers:project', "Enter marker string for project directories")
        self.__user_input(config, 'markers:down', "Enter marker string for disabled projects")

        self.__user_input(config, 'network:name', "Enter name for local docker network")
        self.__user_input(config, 'network:cidr', "Enter CIDR block for local docker network")

        self.__user_input(config, 'runtime:storage', "Enter main directory for local data")

        print(str(config))
