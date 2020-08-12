import logging
import os

from .._constants import KIWI_CONF_NAME
from ..config import DefaultConfig

from ._subcommand import SubCommand


def user_input(config, key, prompt):
    # prompt user as per argument
    try:
        result = input("{} [{}] ".format(prompt, config[key])).strip()
    except EOFError:
        print()
        result = None

    # store result if present
    if result:
        config[key] = result


class InitCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'init',
            description="Create a new kiwi-config instance"
        )

        self._sub_parser.add_argument(
            '-f', '--force',
            action='store_true',
            help=f"use default values even if {KIWI_CONF_NAME} is present"
        )

    def run(self, config, args):
        logging.info(f"Initializing kiwi-config instance in '{os.getcwd()}'")

        if args.force and os.path.isfile(KIWI_CONF_NAME):
            logging.warning(f"Overwriting existing '{KIWI_CONF_NAME}'!")
            config = DefaultConfig.get()

        try:
            # version
            user_input(config, 'version', "Enter kiwi-config version for this instance")

            # runtime
            user_input(config, 'runtime:storage', "Enter local directory for service data")

            # markers
            user_input(config, 'markers:project', "Enter marker string for project directories")
            user_input(config, 'markers:down', "Enter marker string for disabled projects")

            # network
            user_input(config, 'network:name', "Enter name for local docker network")
            user_input(config, 'network:cidr', "Enter CIDR block for local docker network")

            config.save()

        except KeyboardInterrupt:
            print()
            logging.warning(f"'{self}' aborted, input discarded.")
