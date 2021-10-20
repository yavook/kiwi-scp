import logging
import os
from ipaddress import IPv4Network
from pathlib import Path

import click

from .cli import KiwiCTX, pass_kiwi_ctx
from .._constants import KIWI_CONF_NAME
from ..config import Config
from ..misc import user_query


@click.command(
    "init",
    short_help="Initializes kiwi-scp"
)
@click.option(
    "-f/-F",
    "--force/--no-force",
    help=f"use default values even if {KIWI_CONF_NAME} is present",
)
@click.option(
    "-s/-S",
    "--show/--no-show",
    help=f"show effective {KIWI_CONF_NAME} contents instead",
)
@pass_kiwi_ctx
def cmd(ctx: KiwiCTX, force: bool, show: bool):
    """Initialize or reconfigure a kiwi-scp instance"""

    current_config = Config() if force else ctx.config

    if show:
        # just show the currently effective kiwi.yml
        click.echo_via_pager(current_config.kiwi_yml)
        return

    # check force switch
    if force and os.path.isfile(KIWI_CONF_NAME):
        logging.warning(f"Overwriting an existing '{KIWI_CONF_NAME}'!")

    # build new kiwi dict
    kiwi_dict = current_config.kiwi_dict
    kiwi_dict.update({
        "version": user_query("kiwi-scp version to use in this instance", current_config.version),
        "storage": {
            "directory": user_query("local directory for service data", current_config.storage.directory, Path),
        },
        "network": {
            "name": user_query("name for local network hub", current_config.network.name),
            "cidr": user_query("CIDRv4 block for local network hub", current_config.network.cidr, IPv4Network),
        },
    })

    # write out as new kiwi.yml
    with open(ctx.instance.joinpath(KIWI_CONF_NAME), "w") as file:
        file.write(Config.parse_obj(kiwi_dict).kiwi_yml)
