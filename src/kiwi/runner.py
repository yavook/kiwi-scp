# system
import logging

# local
from . import subcommands
from .config import LoadedConfig
from .parser import Parser


class Runner:
    """Singleton: Subcommands setup and run"""

    class __Runner:
        """Singleton type"""

        __parser = None
        __commands = []

        def __init__(self):
            # setup all subcommands
            for className in subcommands.__all__:
                cmd = getattr(subcommands, className)
                self.__commands.append(cmd())

        def run(self):
            """run the desired subcommand"""

            args = Parser().get_args()

            for cmd in self.__commands:
                if str(cmd) == args.command:
                    # command found
                    logging.debug(f"Running '{cmd}' with args: {args}")

                    try:
                        cmd.run(LoadedConfig.get(), args)

                    except KeyboardInterrupt:
                        print()
                        logging.warning(f"'{cmd}' aborted, inputs may have been discarded.")

                    return True

            # command not found
            logging.error(f"kiwi command '{args.command}' unknown")
            return False

    __instance = None

    def __init__(self):
        if Runner.__instance is None:
            # create singleton
            Runner.__instance = Runner.__Runner()

    def __getattr__(self, item):
        """Inner singleton direct access"""

        return getattr(self.__instance, item)
