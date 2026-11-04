from pathlib import Path

from typer.testing import CliRunner

from catalogue_check import __version__
from catalogue_check.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_catalogues_lists_the_configured_ones():
    result = runner.invoke(app, ["catalogues"])
    assert result.exit_code == 0
    assert "bbmri-eric-services" in result.output
    assert "22 catalogue(s): 10 service, 12 research product." in result.output


def test_an_empty_list_is_reported(tmp_path: Path):
    f = tmp_path / "c.yaml"
    f.write_text("catalogues: []\n")
    result = runner.invoke(app, ["catalogues", "--file", str(f)])
    assert result.exit_code == 0
    assert "No catalogues configured yet." in result.output


def test_a_bad_file_is_a_configuration_error(tmp_path: Path):
    f = tmp_path / "c.yaml"
    f.write_text("catalogues:\n  - id: x\n")
    result = runner.invoke(app, ["catalogues", "--file", str(f)])
    assert result.exit_code == 2
