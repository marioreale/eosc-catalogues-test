"""Per-catalogue results for the online report.

Two kinds of result, kept apart:

- configuration checks: what the test suite asserts about catalogues.yaml,
  evaluated entry by entry (no network);
- an availability probe: one HTTP request per endpoint (GET /services for a
  Service Catalogue, ?verb=Identify for an OAI-PMH base URL). An answer shows
  that the endpoint is up and speaks the expected format, nothing about
  compliance or record quality.
"""

from __future__ import annotations

import json
import os
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import httpx

from catalogue_check import __version__
from catalogue_check.config import PROTOCOL_FOR_TYPE, Catalogue

# Node ids and names of eosc-basic-compliance's nodes.yaml (16 nodes).
NODE_NAMES = {
    "bbmri-eric": "BBMRI-ERIC",
    "cern": "CERN",
    "eosc-cz": "EOSC Node Czechia",
    "eosc-dto": "EOSC DTO (D4Science)",
    "data-terra": "Data Terra",
    "eosc-fi": "EOSC Finland",
    "panosc": "PaNOSC",
    "eudat": "EUDAT",
    "egi": "EGI",
    "geant": "GÉANT",
    "eosc-pl": "EOSC Node Poland",
    "eosc-it": "EOSC Node Italy",
    "eosc-sk": "EOSC Node Slovakia",
    "ebrains-ri": "EBRAINS-RI",
    "life-sciences-connect": "Life Sciences Connect",
    "eosc-de": "EOSC Node Germany",
}

SHEET_STATUSES = {"", "NEW", "TESTING", "READY FOR PROD", "REJECTED"}
OAI_NS = "{http://www.openarchives.org/OAI/2.0/}"
TIMEOUT = 20.0


def config_checks(c: Catalogue) -> list[dict]:
    def check(key: str, label: str, passed: bool, detail: str = "") -> dict:
        return {"key": key, "label": label, "passed": passed, "detail": detail}

    out = [
        check("fields", "All required fields present", True,
              "id, node, name, type, protocol, endpoint, source"),
        check("node", "Node is a known EOSC Node", c.node in NODE_NAMES, c.node),
        check("protocol", "Protocol matches catalogue type",
              PROTOCOL_FOR_TYPE.get(c.type) == c.protocol, f"{c.type} → {c.protocol}"),
        check("https", "Endpoint uses HTTPS", c.endpoint.startswith("https://"), c.endpoint),
    ]
    if c.protocol == "oai-pmh":
        out.append(check("oai-base", "OAI-PMH base URL has no ?verb=",
                         "verb=" not in c.endpoint))
    status = c.listed.get("status", "")
    out.append(check("listed", "Sheet status quoted, from the allowed set",
                     status in SHEET_STATUSES, status or "(none)"))
    if c.source == "resource-hub":
        out.append(check("hub", "Resource Hub entry names its Hub record",
                         c.listed == {} and "Hub record 21.11166/" in c.note))
    return out


def _probe_services(r: httpx.Response) -> tuple[bool, str, dict]:
    try:
        body = r.json()
    except ValueError:
        return False, "Answered, but not with JSON", {}
    facts: dict = {}
    if isinstance(body, list):
        facts["items on first page"] = len(body)
    elif isinstance(body, dict):
        for k in ("total", "totalCount", "count"):
            if isinstance(body.get(k), int):
                facts["total declared"] = body[k]
                break
        for k in ("results", "items", "data", "services"):
            if isinstance(body.get(k), list):
                facts["items on first page"] = len(body[k])
                break
    return True, "Answered with JSON", facts


def _probe_oai(r: httpx.Response) -> tuple[bool, str, dict]:
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return False, "Answered, but not with XML", {}
    err = root.find(f"{OAI_NS}error")
    if err is not None:
        return False, f"OAI-PMH error: {err.get('code', '')}", {}
    ident = root.find(f"{OAI_NS}Identify")
    if ident is None:
        return False, "XML without an Identify element", {}
    facts = {}
    for tag in ("repositoryName", "protocolVersion", "baseURL", "earliestDatestamp"):
        el = ident.find(f"{OAI_NS}{tag}")
        if el is not None and el.text:
            facts[tag] = el.text.strip()
    return True, "Answered Identify", facts


def probe(c: Catalogue, client: httpx.Client) -> dict:
    if c.protocol == "oai-pmh":
        url = c.endpoint + ("&" if "?" in c.endpoint else "?") + "verb=Identify"
    else:
        url = c.endpoint
    started = time.monotonic()
    try:
        r = client.get(url)
    except httpx.TimeoutException:
        return {"url": url, "outcome": "timeout", "summary": f"No answer within {TIMEOUT:.0f} s",
                "http_status": None, "seconds": round(time.monotonic() - started, 2), "facts": {},
                "observations": []}
    except httpx.HTTPError as exc:
        return {"url": url, "outcome": "error", "summary": type(exc).__name__,
                "http_status": None, "seconds": round(time.monotonic() - started, 2), "facts": {},
                "observations": []}
    seconds = round(time.monotonic() - started, 2)
    base = {"url": url, "http_status": r.status_code, "seconds": seconds,
            "content_type": r.headers.get("content-type", "")}
    if r.status_code != 200:
        return {**base, "outcome": "fail", "summary": f"HTTP {r.status_code}", "facts": {},
                "observations": []}
    ok, summary, facts = (_probe_oai if c.protocol == "oai-pmh" else _probe_services)(r)
    notes = []
    declared = facts.get("baseURL")
    if declared and declared != c.endpoint:
        notes.append(f"Identify declares baseURL {declared}, not the endpoint queried")
    return {**base, "outcome": "pass" if ok else "fail", "summary": summary, "facts": facts,
            "observations": notes}


def build(catalogues: list[Catalogue], do_probe: bool, tests: dict | None) -> dict:
    rows = []
    client = httpx.Client(timeout=TIMEOUT, follow_redirects=True,
                          headers={"User-Agent": f"eosc-catalogues-test/{__version__}",
                                   "Accept": "application/json, text/xml, */*"})
    with client:
        for c in catalogues:
            rows.append({
                **asdict(c),
                "node_name": NODE_NAMES.get(c.node, c.node),
                "checks": config_checks(c),
                "probe": probe(c, client) if do_probe else None,
            })
    return {
        "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": __version__,
        "tests": tests,
        "commit": os.environ.get("GITHUB_SHA", ""),
        "run_url": (
            f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
            f"/actions/runs/{os.environ['GITHUB_RUN_ID']}"
            if os.environ.get("GITHUB_RUN_ID") else ""
        ),
        "catalogues": rows,
    }


def junit_summary(path: Path) -> dict:
    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    cases = []
    for tc in suite.iter("testcase"):
        outcome = "passed"
        if tc.find("failure") is not None or tc.find("error") is not None:
            outcome = "failed"
        elif tc.find("skipped") is not None:
            outcome = "skipped"
        cases.append({"name": tc.get("name"), "file": tc.get("classname"), "outcome": outcome})
    return {
        "total": len(cases),
        "passed": sum(c["outcome"] == "passed" for c in cases),
        "failed": sum(c["outcome"] == "failed" for c in cases),
        "skipped": sum(c["outcome"] == "skipped" for c in cases),
        "cases": cases,
    }


def write(data: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
