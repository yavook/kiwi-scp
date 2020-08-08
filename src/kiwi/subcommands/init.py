import logging
import os

from ..core import KIWI_CONF_NAME, Parser
from ..config import DefaultConfig

from ._utils import SubCommand


def user_input(config, key, prompt):
    # prompt user as per argument
    result = input("{} [Default: {}] ".format(prompt, config[key])).strip()

    # store result if present
    if result:
        config[key] = result


def find_exe(program_name):
    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, program_name)
        if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
            return exe_file

    return None


def user_input_exe(config, program_name):
    exe_file = find_exe(program_name)
    key = 'executables:' + program_name

    if exe_file is not None:
        config[key] = exe_file
    else:
        user_input(config, key, "Enter path to '{}' executable".format(program_name))


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
        config = DefaultConfig.get()

        if os.path.isfile(KIWI_CONF_NAME):
            logging.warning("Overwriting existing '%s'!", KIWI_CONF_NAME)

        user_input(config, 'version', "Choose kiwi-config version")

        user_input(config, 'runtime:storage', "Enter main directory for local data")

        user_input(config, 'markers:project', "Enter marker string for project directories")
        user_input(config, 'markers:down', "Enter marker string for disabled projects")

        user_input(config, 'network:name', "Enter name for local docker network")
        user_input(config, 'network:cidr', "Enter CIDR block for local docker network")

        user_input_exe(config, 'docker')
        user_input_exe(config, 'docker-compose')
        user_input_exe(config, 'sudo')

        config.save()
