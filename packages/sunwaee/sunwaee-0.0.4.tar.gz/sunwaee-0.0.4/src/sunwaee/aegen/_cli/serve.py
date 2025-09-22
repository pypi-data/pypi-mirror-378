# standard
import sys
import typing

# third party
import typer
import uvicorn

# custom
from sunwaee.aegen._cli._entrypoint import aegen_commands


@aegen_commands.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
    reload: bool = typer.Option(False, "--reload", "-r"),
    workers: int | None = typer.Option(None, "--workers", "-w"),
    log_level: typing.Literal[
        "debug", "info", "warning", "error", "critical"
    ] = typer.Option("info", "--log-level", "-l", case_sensitive=False),
):
    """
    Serve the æ-gen API.

    Examples:
    - sunwaee aegen serve
    - sunwaee aegen serve --host 0.0.0.0 --port 8080
    - sunwaee aegen serve --reload --log-level debug
    """

    if workers and reload:
        workers = None

    try:
        uvicorn.run(
            "sunwaee.api:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level.lower(),
        )
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        sys.exit(1)
