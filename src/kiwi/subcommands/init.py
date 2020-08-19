# system
import logging
import os

# local
from ._subcommand import SubCommand

# parent (display purposes only)
from .._constants import KIWI_CONF_NAME
from ..config import DefaultConfig, LoadedConfig


def user_input(config, key, prompt):
    """query user for new config value"""

    # prompt user as per argument
    try:
        result = input(f"{prompt} [{config[key]}] ").strip()
    except EOFError:
        print()
        result = None

    # store result if present
    if result:
        config[key] = result


class InitCommand(SubCommand):
    """kiwi init"""

    def __init__(self):
        super().__init__(
            'init',
            action="Creating",
            description="Create a new kiwi-config instance"
        )

        # -f switch: Initialize with default config
        self._sub_parser.add_argument(
            '-f', '--force',
            action='store_true',
            help=f"use default values even if {KIWI_CONF_NAME} is present"
        )

    def _run_instance(self, runner, args):
        logging.info(f"Initializing '{KIWI_CONF_NAME}' in '{os.getcwd()}'")
        config = LoadedConfig.get()

        # check force switch
        if args.force and os.path.isfile(KIWI_CONF_NAME):

            logging.warning(f"Overwriting existing '{KIWI_CONF_NAME}'!")
            config = DefaultConfig.get()

        # version
        user_input(config, 'version', "Enter kiwi-config version for this instance")

        # runtime
        user_input(config, 'runtime:storage', "Enter local directory for service data")

        # markers
        user_input(config, 'markers:project', "Enter marker string for project directories")
        user_input(config, 'markers:disabled', "Enter marker string for disabled projects")

        # network
        user_input(config, 'network:name', "Enter name for local docker network")
        user_input(config, 'network:cidr', "Enter CIDR block for local docker network")

        config.save()
        return True
