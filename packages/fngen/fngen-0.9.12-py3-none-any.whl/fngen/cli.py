from fngen.commands.project import project_app
import time
import typer
from rich.console import Console
from rich import print as rprint
import sys
from art import text2art
import typer.models
from importlib.metadata import version, PackageNotFoundError

from fngen.api_key_manager import NoAPIKeyError, get_api_key
from fngen.cli_util import help_option, print_custom_help

from fngen.commands.login import login

from fngen.commands.whoami import whoami

from fngen.commands.push import push, simulate_push, watch_pipeline

from fngen.commands.logs import logs

app = typer.Typer(add_help_option=False, add_completion=False)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    help: bool = help_option
):
    if ctx.invoked_subcommand is None:
        print_custom_help(ctx)
        raise typer.Exit()


app.command(name="login", help="Log in + set up your API key")(login)

app.command(name="whoami", help="Test your API key")(whoami)

app.command(name="push",  help="Push a deployment package")(push)

# app.command(name="watch",  help="Push a deployment package")(watch_pipeline)


# app.command(name="sim",  help="Push ux sim")(simulate_push)

app.command(name="logs",  help="Stream logs")(logs)


app.add_typer(project_app, name="project")


@app.command(name="version", help="Print fngen version")
def _version(help: bool = help_option):
    """Prints the package version."""
    try:
        try:
            __version__ = version("fngen")
        except PackageNotFoundError:
            __version__ = "unknown (package not installed)"
    except ImportError:
        __version__ = "unknown (importlib.metadata not available)"

    rprint(f"[bold]fngen[/bold] version: [yellow]{__version__}[/yellow]")


if __name__ == "__main__":
    app()
