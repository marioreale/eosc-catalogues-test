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
    if c.source == "resource-hub":
        out.append(check("source", "Resource Hub entry names its Hub record",
                         c.listed == {} and "Hub record 21.11166/" in c.note, c.source))
    else:
        out.append(check("source", "Endpoint taken from the production sheet",
                         c.source == "production", c.source))
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


TYPE_LABELS = {"service-catalogue": "Service", "research-product-catalogue": "Research product"}
PAGE_URL = "https://marioreale.github.io/eosc-catalogues-test/"


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def _probe_cell(p: dict | None) -> str:
    if not p:
        return "not probed"
    if p["outcome"] == "pass":
        verdict = "Up · note" if p.get("observations") else "Up"
    elif p["outcome"] == "timeout":
        verdict = "Timeout"
    else:
        verdict = "Down"
    status = f"HTTP {p['http_status']} · " if p.get("http_status") else ""
    return f"{verdict} ({status}{p['seconds']} s)"


def markdown(data: dict) -> str:
    """The results as Markdown, for reading on GitHub next to the copy of the page."""
    rows = data["catalogues"]
    probed = [r for r in rows if r["probe"]]
    up = sum(r["probe"]["outcome"] == "pass" for r in probed)
    checks = [c for r in rows for c in r["checks"]]
    lines = [
        "# Results",
        "",
        f"The same results as the [results page]({PAGE_URL}). This directory holds a copy",
        "of that page, updated by the `results page` workflow on every run: `index.html`,",
        "its scripts, styles and logos, and `results.json`. GitHub shows the HTML as source;",
        "to see the page from a clone, run `python3 -m http.server -d results` and open",
        "<http://localhost:8000/> (the page reads `results.json`, which browsers do not",
        "load from a file opened directly). The table below gives the same results.",
        "",
        f"Generated {data['generated']}"
        + (f" from commit `{data['commit'][:7]}`" if data.get("commit") else "")
        + (f" ([CI run]({data['run_url']}))" if data.get("run_url") else "") + ".",
        "",
        f"- Catalogues: {len(rows)} from {len({r['node'] for r in rows})} nodes",
        f"- Configuration checks passed: {sum(c['passed'] for c in checks)} of {len(checks)}",
        f"- Endpoints that answered the probe: {up} of {len(probed)}",
    ]
    t = data.get("tests")
    if t:
        lines.append(f"- Tests: {t['passed']} passed, {t['failed']} failed, "
                     f"{t['skipped']} skipped, of {t['total']}")
    lines += ["", "| Node | Catalogue | Type | Checks | Probe | Notes |",
              "|---|---|---|---|---|---|"]
    for r in rows:
        ok = sum(c["passed"] for c in r["checks"])
        endpoint = r.get("display_endpoint") or r["endpoint"]
        notes = _cell("; ".join((r["probe"] or {}).get("observations") or []))
        kind = TYPE_LABELS.get(r["type"], r["type"])
        lines.append(
            f"| {_cell(r['node_name'])} | [{_cell(r['name'])}]({endpoint}) | {kind}"
            f" | {ok}/{len(r['checks'])} | {_probe_cell(r['probe'])} | {notes} |")
    lines += ["", "A green probe only means the endpoint is up and speaks the expected format;",
              "none of this is a compliance verdict.", ""]
    return "\n".join(lines)
