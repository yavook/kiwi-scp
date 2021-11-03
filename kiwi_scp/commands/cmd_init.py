import logging
import os
from ipaddress import IPv4Network
from pathlib import Path

import click

from .cli import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from .._constants import KIWI_CONF_NAME
from ..config import KiwiConfig
from ..instance import Instance

_logger = logging.getLogger(__name__)


@click.option(
    "-d",
    "--directory",
    help=f"initialize a kiwi-scp instance in another directory",
    type=click.Path(
        path_type=Path,
        dir_okay=True,
        writable=True,
    ),
)
@click.option(
    "-f/-F",
    "--force/--no-force",
    help=f"use default values even if {KIWI_CONF_NAME} is present",
)
@kiwi_command(
    "init",
    KiwiCommandType.INSTANCE,
    short_help="Initializes kiwi-scp",
)
class CMD(KiwiCommand):
    """Initialize or reconfigure a kiwi-scp instance"""

    @classmethod
    def run_for_instance(cls, instance: Instance, output: Path = None, force: bool = None, **kwargs) -> None:
        if output is not None:
            instance.directory = output

        current_config = KiwiConfig() if force else instance.config

        # check force switch
        if force and os.path.isfile(KIWI_CONF_NAME):
            _logger.warning(f"About to overwrite an existing '{KIWI_CONF_NAME}'!")

        # build new kiwi dict
        kiwi_dict = current_config.kiwi_dict
        kiwi_dict.update({
            "version": KiwiCommand.user_query("kiwi-scp version to use in this instance", current_config.version),
            "storage": {
                "directory": KiwiCommand.user_query("local directory for service data",
                                                    current_config.storage.directory, Path),
            },
            "network": {
                "name": KiwiCommand.user_query("name for local network hub", current_config.network.name),
                "cidr": KiwiCommand.user_query("CIDRv4 block for local network hub", current_config.network.cidr,
                                               IPv4Network),
            },
        })

        # ensure output directory exists
        if not os.path.isdir(instance.directory):
            os.mkdir(instance.directory)

        # write out the new kiwi.yml
        cfg = KiwiConfig.parse_obj(kiwi_dict)
        with open(instance.directory.joinpath(KIWI_CONF_NAME), "w") as file:
            cfg.dump_kiwi_yml(file)
