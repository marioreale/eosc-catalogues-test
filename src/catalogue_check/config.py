"""Load and validate catalogues.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import yaml

TYPES = {"service-catalogue", "research-product-catalogue"}
PROTOCOLS = {"een-services-api", "oai-pmh"}
# A Service Catalogue is queried through the EEN services API, a Research
# Product Catalogue through OAI-PMH; any other pairing is a configuration slip.
PROTOCOL_FOR_TYPE = {
    "service-catalogue": "een-services-api",
    "research-product-catalogue": "oai-pmh",
}
REQUIRED = ("id", "node", "name", "type", "protocol", "endpoint", "source")


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Catalogue:
    id: str
    node: str
    name: str
    type: str
    protocol: str
    endpoint: str
    source: str
    website: str = ""
    note: str = ""
    listed: dict = field(default_factory=dict)


def load(path: Path) -> list[Catalogue]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("catalogues") or []
    out: list[Catalogue] = []
    seen: set[str] = set()
    for i, e in enumerate(entries):
        where = f"{path}: entry {i + 1}"
        missing = [k for k in REQUIRED if not e.get(k)]
        if missing:
            raise ConfigError(f"{where}: missing {', '.join(missing)}")
        if e["id"] in seen:
            raise ConfigError(f"{where}: duplicate id {e['id']!r}")
        seen.add(e["id"])
        if e["type"] not in TYPES:
            raise ConfigError(f"{where}: unknown type {e['type']!r}")
        if e["protocol"] not in PROTOCOLS:
            raise ConfigError(f"{where}: unknown protocol {e['protocol']!r}")
        if PROTOCOL_FOR_TYPE[e["type"]] != e["protocol"]:
            expected = PROTOCOL_FOR_TYPE[e["type"]]
            raise ConfigError(f"{where}: a {e['type']} is queried with {expected}")
        parts = urlsplit(e["endpoint"])
        if parts.scheme != "https" or not parts.netloc or " " in e["endpoint"]:
            raise ConfigError(f"{where}: endpoint must be an absolute https URL")
        if e["protocol"] == "oai-pmh" and "verb=" in parts.query:
            raise ConfigError(f"{where}: give the OAI-PMH base URL, without ?verb=")
        out.append(
            Catalogue(
                **{k: e[k] for k in REQUIRED},
                website=e.get("website") or "",
                note=e.get("note") or "",
                listed=e.get("listed") or {},
            )
        )
    return out
