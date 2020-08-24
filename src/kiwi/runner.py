# system
import logging
import subprocess

# local
from . import subcommands
from .executable import Executable
from .parser import Parser


class Runner:
    """Singleton: Subcommands setup and run"""

    class __Runner:
        """Singleton type"""

        __commands = []

        def __init__(self):
            # probe for Docker access
            try:
                Executable('docker').run([
                    'ps'
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            except subprocess.CalledProcessError:
                logging.critical("Cannot access docker, please get into the docker group or run as root!")
                quit(1)

            # setup all subcommands
            for className in subcommands.__all__:
                cmd = getattr(subcommands, className)
                self.__commands.append(cmd())

        def run(self, command=None, args=None):
            """run the desired subcommand"""

            if args is None:
                args = Parser().get_args()

            if command is None:
                command = args.command

            for cmd in self.__commands:
                if str(cmd) == command:
                    # command found
                    logging.debug(f"Running '{cmd}' with args: {args}")

                    try:
                        result = cmd.run(self, args)

                    except KeyboardInterrupt:
                        print()
                        logging.warning(f"'{cmd}' aborted, inputs may have been discarded.")
                        result = False

                    return result

            # command not found
            logging.error(f"kiwi command '{command}' unknown")
            return False

    __instance = None

    def __init__(self):
        if Runner.__instance is None:
            # create singleton
            Runner.__instance = Runner.__Runner()

    def __getattr__(self, item):
        """Inner singleton direct access"""

        return getattr(self.__instance, item)
