import logging
import os

from ..core import KIWI_CONF_NAME, Parser
from ..config import DefaultConfig, LoadedConfig

from ._utils import SubCommand


def user_input(config, key, prompt):
    # prompt user as per argument
    result = input("{} [{}] ".format(prompt, config[key])).strip()

    # store result if present
    if result:
        config[key] = result


def is_executable(filename):
    if filename is None:
        return False

    return os.path.isfile(filename) and os.access(filename, os.X_OK)


def find_exe(program_name):
    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, program_name)
        if is_executable(exe_file):
            return exe_file

    return None


def user_input_exe(config, key):
    exe_file = config[key]
    program_name = key.split(':')[1]

    if not is_executable(exe_file):
        logging.info("Reconfiguring '%s' executable path.", program_name)
        exe_file = find_exe(program_name)

        if exe_file is not None:
            logging.debug("Found executable at '%s'.", exe_file)
            config[key] = exe_file
        else:
            user_input(config, key, f"Enter path to '{program_name}' executable")


class InitCommand(SubCommand):
    command = 'init'

    @classmethod
    def setup(cls):
        parser = Parser.get_subparsers().add_parser(
            cls.command,
            description="Create a new kiwi-config instance"
        )

        parser.add_argument(
            '-f', '--force',
            action='store_true',
            help=f"Use default values even if {KIWI_CONF_NAME} is present"
        )

    @classmethod
    def run(cls):
        logging.info(f"Initializing kiwi-config instance in '{os.getcwd()}'")

        if Parser.get_args().force and os.path.isfile(KIWI_CONF_NAME):
            logging.warning("Overwriting existing '%s'!", KIWI_CONF_NAME)
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
        user_input_exe(config, 'executables:docker')
        user_input_exe(config, 'executables:docker-compose')
        user_input_exe(config, 'executables:sudo')

        config.save()
