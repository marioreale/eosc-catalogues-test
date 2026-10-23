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
    assert len(CATALOGUES) == 16
    assert sum(c.type == "service-catalogue" for c in CATALOGUES) == 7


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


def test_listed_status_is_quoted_not_judged():
    allowed = {"", "NEW", "TESTING", "READY FOR PROD", "REJECTED"}
    for c in CATALOGUES:
        assert c.listed.get("status", "") in allowed, c.id


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
