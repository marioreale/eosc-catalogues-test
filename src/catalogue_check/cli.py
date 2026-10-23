"""Command line entry point.

Planned phases, mirroring eosc-basic-compliance: `collect` queries each
catalogue endpoint and stores the raw responses as evidence; `assess` derives
verdicts offline from that evidence; `report` renders HTML, Markdown, CSV and
JSON. Only `version` and `catalogues` exist so far.
"""

from pathlib import Path

import typer
import yaml

from catalogue_check import __version__

app = typer.Typer(add_completion=False, help="Query, check and assess EOSC Node catalogues.")

DEFAULT_CATALOGUES = Path("catalogues.yaml")


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo(__version__)


@app.command()
def catalogues(
    file: Path = typer.Option(DEFAULT_CATALOGUES, "--file", help="Catalogue configuration."),
) -> None:
    """List the configured catalogues (none yet)."""
    data = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
    entries = data.get("catalogues") or []
    if not entries:
        typer.echo("No catalogues configured yet.")
        return
    for c in entries:
        typer.echo(f"{c['id']:24} {c.get('type', '?'):28} {c.get('endpoint', '')}")
