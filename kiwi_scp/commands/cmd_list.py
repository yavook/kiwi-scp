import click

from kiwi_scp.misc import service_command


@click.command(
    "list",
    short_help="Inspect a kiwi-scp instance",
)
@service_command
def cmd(project: str, service: str):
    """List projects in this instance, services inside a project or service(s) inside a project"""
    print(f"project: {project!r}, service: {service!r}")
