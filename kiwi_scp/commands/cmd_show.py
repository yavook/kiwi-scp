from pathlib import Path

import click

from kiwi_scp.misc import service_command


@click.command()
@service_command
def cmd(project: str, service: str):
    project = str(Path(project))
    print(f"project: {project!r}, service: {service!r}")
