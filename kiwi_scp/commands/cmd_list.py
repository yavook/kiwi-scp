from typing import Tuple

import click

from ..instance import Instance, pass_instance
from ..misc import service_command


@click.command(
    "list",
    short_help="Inspect a kiwi-scp instance",
)
@pass_instance
@service_command
def cmd(ctx: Instance, project: str, services: Tuple[str]):
    """List projects in this instance, services inside a project or service(s) inside a project"""
    if project is not None:
        print(ctx.get_services(project, services))
    else:
        print(f"projects: {ctx.config.projects}")
