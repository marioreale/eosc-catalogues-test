"""Command line entry point.

Planned phases, mirroring eosc-basic-compliance: `collect` queries each
catalogue endpoint and stores the raw responses as evidence; `assess` derives
verdicts offline from that evidence; `report` renders HTML, Markdown, CSV and
JSON. Only `version` and `catalogues` (list and validate catalogues.yaml)
exist so far.
"""

from pathlib import Path

import typer

from catalogue_check import __version__
from catalogue_check.config import ConfigError, load

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
    """List the configured catalogues."""
    try:
        entries = load(file)
    except ConfigError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        raise typer.Exit(2) from exc
    if not entries:
        typer.echo("No catalogues configured yet.")
        return
    for c in entries:
        typer.echo(f"{c.id:24} {c.node:12} {c.protocol:17} {c.endpoint}")
    services = sum(c.type == "service-catalogue" for c in entries)
    typer.echo(
        f"\n{len(entries)} catalogue(s): {services} service, "
        f"{len(entries) - services} research product."
    )


@app.command()
def report(
    file: Path = typer.Option(DEFAULT_CATALOGUES, "--file", help="Catalogue configuration."),
    out: Path = typer.Option(Path("site/results.json"), "--out", help="Where to write the JSON."),
    probe: bool = typer.Option(True, "--probe/--no-probe", help="Send one request per endpoint."),
    junit: Path | None = typer.Option(None, "--junit", help="pytest JUnit XML to include."),
) -> None:
    """Write per-catalogue results (configuration checks and availability probe) as JSON."""
    from catalogue_check import report as rep

    try:
        entries = load(file)
    except ConfigError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        raise typer.Exit(2) from exc
    tests = rep.junit_summary(junit) if junit and junit.exists() else None
    data = rep.build(entries, probe, tests)
    rep.write(data, out)
    answered = sum((r["probe"] or {}).get("outcome") == "pass" for r in data["catalogues"])
    typer.echo(f"Wrote {out}: {len(entries)} catalogue(s)"
               + (f", {answered} answered the probe." if probe else "."))
