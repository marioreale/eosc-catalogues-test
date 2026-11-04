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


def test_report_without_probe_writes_per_catalogue_checks(tmp_path: Path):
    import json

    out = tmp_path / "results.json"
    result = runner.invoke(app, ["report", "--no-probe", "--out", str(out)])
    assert result.exit_code == 0, result.output
    data = json.loads(out.read_text())
    assert len(data["catalogues"]) == 22
    for row in data["catalogues"]:
        assert row["probe"] is None
        assert row["node_name"]
        assert all(c["passed"] for c in row["checks"]), row["id"]
