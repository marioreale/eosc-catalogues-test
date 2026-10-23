from typer.testing import CliRunner

from catalogue_check import __version__
from catalogue_check.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_no_catalogues_configured_yet():
    result = runner.invoke(app, ["catalogues"])
    assert result.exit_code == 0
    assert "No catalogues configured yet." in result.output
