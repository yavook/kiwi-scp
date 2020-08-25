# system
import logging
import os

# local
from .._constants import KIWI_CONF_NAME
from ..subcommand import SubCommand
from ..config import DefaultConfig, LoadedConfig


class InitCommand(SubCommand):
    """kiwi init"""

    def __init__(self):
        super().__init__(
            'init',
            action=f"Initializing '{KIWI_CONF_NAME}' in",
            description="Initialize or reconfigure kiwi-config instance"
        )

        # -f switch: Initialize with default config
        self._sub_parser.add_argument(
            '-f', '--force',
            action='store_true',
            help=f"use default values even if {KIWI_CONF_NAME} is present"
        )

        # -s switch: Show current config instead
        self._sub_parser.add_argument(
            '-s', '--show',
            action='store_true',
            help=f"show effective {KIWI_CONF_NAME} contents instead"
        )

    def _run_instance(self, runner, args):
        config = LoadedConfig.get()

        # check show switch
        if args.show:
            print(config)
            return True

        # check force switch
        if args.force and os.path.isfile(KIWI_CONF_NAME):

            logging.warning(f"Overwriting existing '{KIWI_CONF_NAME}'!")
            config = DefaultConfig.get()

        # version
        config.user_query('version')

        # runtime
        config.user_query('runtime:storage')

        # markers
        config.user_query('markers:project')
        config.user_query('markers:disabled')

        # network
        config.user_query('network:name')
        config.user_query('network:cidr')

        config.save()
        return True
