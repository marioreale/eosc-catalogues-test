# eosc-catalogues-test

Queries the **Service Catalogues** and **Research Product (Resource) Catalogues**
of EOSC Nodes, checks them for compliance, and assesses the content of their
records.

It is a sibling of
[eosc-basic-compliance](https://github.com/marioreale/eosc-basic-compliance),
which checks Node Landing Pages, and uses the same technologies: Python for
collection and checks, HTML (with Markdown, CSV and JSON) for the reports.

## Scope

1. **Query.** Read each node's catalogue through its public endpoint, the one
   registered as a Data Source with the EOSC EU Node, and store the raw
   responses as evidence.
2. **Compliance.** Check the endpoint and its records against the technical
   contract: for a Service Catalogue, `GET /services` and records that map to
   the Service Bundle schema with its mandatory fields, as set out in the EOSC
   EU Node interoperability guidelines. Where a node also publishes DCAT or
   DCAT-AP, that profile is checked separately.
3. **Content.** Assess what the records say: whether mandatory fields are
   filled in with meaningful values, whether service-level terms of use and
   access policy URLs are present and resolve, and how the catalogue compares
   with what the node declares elsewhere.

## Principles, as in eosc-basic-compliance

- **Evidence first.** Collection is the only phase that touches the network;
  every verdict is derived offline from stored evidence and can be re-derived.
- **Separate scopes.** Technical conformance of a catalogue, a node's
  declarations and the checklist's policy requirements are different questions,
  with separate verdicts. A valid response does not show that a catalogue is in
  production or has been harvested.
- **Human review where needed.** Results the tool cannot decide are marked for
  review, not passed or failed.

## Status

`catalogues.yaml` lists the first **16 catalogues of 11 nodes**: 7 Service
Catalogues queried through the EOSC EU Node services API (`GET /services`) and
9 Research Product Catalogues queried through OAI-PMH. The endpoints come from
two sheets shared in October 2026: the EOSC EU Node enrolment list
("Catalogues status") and the production-environment sheet. Each entry quotes
what the sheet says about it (`listed`), without judging it. Each endpoint was
sent one request on 23 October 2026: all answered except the two Italian IRIS
OAI-PMH servers, which timed out at 20 s. An answer shows only that the
endpoint is up, nothing about compliance. No check exists yet.

| Node | Service Catalogue | Research Product Catalogue(s) |
|---|---|---|
| BBMRI-ERIC | `eosc-catalogue.bbmri-eric.eu/services` | `eosc-catalogue.bbmri-eric.eu/oai` |
| CERN | | CERN Open Data (`opendata.cern/oai2d`) |
| Czechia | | National Metadata Directory (`test1.nma.du.cesnet.cz/oai2d`) |
| Data Terra | `services.earth-data.eu/services` | `resources.earth-data.eu/oai` |
| DTO | `gcat.d4science.org/.../EOSC-Node-DTO/services` | Zenodo community (`zenodo.org/oai2d`, set to be identified) |
| EUDAT | `portal.eudat.eu/api/services` | B2FIND (`b2find.eudat.eu/oai`) |
| Finland | `data.eosc.fi/v1/services` | |
| GÉANT | `geant-node-catalogue.geant.org/services` | |
| Italy | | CNR IRIS, IRIS AperTO (UniTo) (`/oai/openaire4`) |
| PaNOSC | | RODARE (`rodare.hzdr.de/oai2d`) |
| Slovakia | `sc.eosc.sk/api/v1/services` | |

Not yet included: catalogues the sheets list without an endpoint (for example
EGI, Italy's and PaNOSC's Service Catalogues, DTO's Blue-Cloud), and catalogues
listed as REJECTED.

```bash
uv sync
uv run catalogue-check version
uv run catalogue-check catalogues   # list and validate catalogues.yaml
uv run pytest -q
```
