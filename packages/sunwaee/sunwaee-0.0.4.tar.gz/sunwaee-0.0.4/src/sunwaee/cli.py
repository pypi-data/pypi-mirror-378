# standard
# third party
import typer

# custom
from sunwaee.aegen._cli._entrypoint import aegen_commands

cli_app = typer.Typer(
    name="sunwaee",
    help="The almost-everything CLI.",
    rich_markup_mode="rich",
)


def main():
    cli_app()


cli_app.add_typer(aegen_commands, name="aegen")
