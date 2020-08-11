import logging
import os

from ..core import KIWI_CONF_NAME, Parser
from ..config import DefaultConfig, LoadedConfig

from ._utils import SubCommand, is_executable, find_exe_file, get_exe_key


def user_input(config, key, prompt):
    # prompt user as per argument
    result = input("{} [{}] ".format(prompt, config[key])).strip()

    # store result if present
    if result:
        config[key] = result


def user_input_exe(config, exe_name):
    key = get_exe_key(exe_name)
    exe_file = config[key]

    if not is_executable(exe_file):
        logging.info(f"Reconfiguring '{exe_name}' executable path.")
        exe_file = find_exe_file(exe_name)

        if exe_file is not None:
            logging.debug(f"Found executable at '{exe_file}'.")
            config[key] = exe_file
        else:
            user_input(config, key, f"Enter path to '{exe_name}' executable")


class InitCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'init',
            description="Create a new kiwi-config instance"
        )

        self._parser.add_argument(
            '-f', '--force',
            action='store_true',
            help=f"use default values even if {KIWI_CONF_NAME} is present"
        )

    def run(self):
        logging.info(f"Initializing kiwi-config instance in '{os.getcwd()}'")

        if Parser().get_args().force and os.path.isfile(KIWI_CONF_NAME):
            logging.warning(f"Overwriting existing '{KIWI_CONF_NAME}'!")
            config = DefaultConfig.get()
        else:
            config = LoadedConfig.get()

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

        # executables
        user_input_exe(config, 'docker')
        user_input_exe(config, 'docker-compose')
        user_input_exe(config, 'sudo')

        config.save()
