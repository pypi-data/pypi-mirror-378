# standard
# third party
import typer

# custom

aegen_commands = typer.Typer(
    name="aegen",
    help="Sunwæe æ-gen commands",
    rich_markup_mode="rich",
)

from . import list
from . import serve

aegen_commands.add_typer(list.list_subcommands, name="list")
