# standard
# third party
import typer

# custom
from sunwaee.aegen import AGENTS, MODELS, PROVIDERS

list_subcommands = typer.Typer(
    name="list",
    help="List available providers, models, agents...",
    rich_markup_mode="rich",
)


@list_subcommands.command("models")
def list_models():
    """List available models."""
    for model_name in sorted(MODELS.keys()):
        typer.echo(model_name)


@list_subcommands.command("providers")
def list_providers():
    """List available providers."""
    for provider_name in sorted(PROVIDERS.keys()):
        typer.echo(provider_name)


@list_subcommands.command("agents")
def list_agents():
    """List available agents."""
    for agent_name in sorted(AGENTS.keys()):
        typer.echo(agent_name)
