import logging
import os
from ipaddress import IPv4Network
from pathlib import Path

import click

from .._constants import KIWI_CONF_NAME
from ..config import KiwiConfig
from ..instance import Instance, pass_instance
from ..misc import user_query


@click.command(
    "init",
    short_help="Initializes kiwi-scp",
)
@click.option(
    "-o",
    "--output",
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
@click.option(
    "-s/-S",
    "--show/--no-show",
    help=f"show effective {KIWI_CONF_NAME} contents instead",
)
@pass_instance
def cmd(ctx: Instance, output: Path, force: bool, show: bool):
    """Initialize or reconfigure a kiwi-scp instance"""

    if output is not None:
        ctx.directory = output

    current_config = KiwiConfig() if force else ctx.config

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

    # ensure output directory exists
    if not os.path.isdir(ctx.directory):
        os.mkdir(ctx.directory)

    # write out the new kiwi.yml
    with open(ctx.directory.joinpath(KIWI_CONF_NAME), "w") as file:
        KiwiConfig.parse_obj(kiwi_dict).dump_kiwi_yml(file)
