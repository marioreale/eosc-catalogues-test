"""The committed catalogues.yaml, and the validation that guards it."""

from pathlib import Path

import pytest

from catalogue_check.config import PROTOCOL_FOR_TYPE, ConfigError, load

ROOT = Path(__file__).resolve().parents[1]
CATALOGUES = load(ROOT / "catalogues.yaml")

# Node ids of eosc-basic-compliance's nodes.yaml (16 nodes, 20 October 2026).
# Catalogue entries must use the same ids so the two projects can be joined.
KNOWN_NODES = {
    "bbmri-eric", "cern", "eosc-cz", "eosc-dto", "data-terra", "eosc-fi", "panosc",
    "eudat", "egi", "geant", "eosc-pl", "eosc-it", "eosc-sk", "ebrains-ri",
    "life-sciences-connect", "eosc-de",
}


def test_the_first_catalogues_are_configured():
    assert len(CATALOGUES) == 22
    assert sum(c.type == "service-catalogue" for c in CATALOGUES) == 10
    assert len({c.node for c in CATALOGUES}) == 13


def test_ids_are_unique_and_nodes_are_known():
    ids = [c.id for c in CATALOGUES]
    assert len(ids) == len(set(ids))
    assert {c.node for c in CATALOGUES} <= KNOWN_NODES


def test_type_and_protocol_agree():
    for c in CATALOGUES:
        assert PROTOCOL_FOR_TYPE[c.type] == c.protocol, c.id


def test_endpoints_are_https_and_oai_bases_have_no_verb():
    for c in CATALOGUES:
        assert c.endpoint.startswith("https://"), c.id
        if c.protocol == "oai-pmh":
            assert "verb=" not in c.endpoint, c.id


def test_every_entry_comes_from_the_production_sheet_but_poland():
    for c in CATALOGUES:
        expected = "resource-hub" if c.node == "eosc-pl" else "production"
        assert c.source == expected, c.id
        assert set(c.listed) <= {"comment", "evaluation_eosc_a"}, c.id


def test_resource_hub_entries_quote_nothing_and_name_their_record():
    hub = [c for c in CATALOGUES if c.source == "resource-hub"]
    assert len(hub) == 3
    for c in hub:
        assert c.listed == {}, c.id
        assert "Hub record 21.11166/" in c.note, c.id


def test_a_display_endpoint_is_explained_in_the_note():
    shown = [c for c in CATALOGUES if c.display_endpoint]
    assert [c.id for c in shown] == ["eosc-cz-nmd-oai"]
    for c in shown:
        assert c.display_endpoint != c.endpoint
        assert c.display_endpoint in c.note and c.endpoint in c.note


def _write(tmp_path, body):
    f = tmp_path / "c.yaml"
    f.write_text(body)
    return f


ENTRY = """catalogues:
  - id: a
    node: eudat
    name: A
    type: {type}
    protocol: {protocol}
    endpoint: {endpoint}
    source: test
"""


@pytest.mark.parametrize(
    "type_, protocol, endpoint, message",
    [
        ("service-catalogue", "oai-pmh", "https://x.example/services", "queried with"),
        ("dataset-catalogue", "oai-pmh", "https://x.example/oai", "unknown type"),
        ("service-catalogue", "een-services-api", "http://x.example/services", "https URL"),
        (
            "research-product-catalogue", "oai-pmh",
            "https://x.example/oai?verb=Identify", "without ?verb=",
        ),
    ],
)
def test_bad_entries_are_rejected(tmp_path, type_, protocol, endpoint, message):
    f = _write(tmp_path, ENTRY.format(type=type_, protocol=protocol, endpoint=endpoint))
    with pytest.raises(ConfigError, match=message.replace("?", r"\?")):
        load(f)


def test_duplicate_ids_are_rejected(tmp_path):
    one = ENTRY.format(
        type="service-catalogue", protocol="een-services-api", endpoint="https://x.example/s"
    )
    body = one + one.split("catalogues:\n", 1)[1]
    with pytest.raises(ConfigError, match="duplicate id"):
        load(_write(tmp_path, body))


def test_unknown_listed_fields_are_rejected(tmp_path):
    body = ENTRY.format(
        type="service-catalogue", protocol="een-services-api", endpoint="https://x.example/s"
    ) + "    listed: {status: READY FOR PROD}\n"
    with pytest.raises(ConfigError, match="unknown listed field"):
        load(_write(tmp_path, body))


def test_every_known_node_has_a_display_name():
    from catalogue_check.report import NODE_NAMES

    assert set(NODE_NAMES) == KNOWN_NODES
