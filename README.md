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

`catalogues.yaml` lists **22 catalogues of 13 nodes**: 10 Service Catalogues
queried through the EOSC EU Node services API (`GET /services`) and 12 Research
Product Catalogues queried through OAI-PMH.

- **16 come from two sheets** shared in October 2026: the EOSC EU Node
  enrolment list ("Catalogues status") and the production-environment sheet.
  Each of these entries quotes what the sheet says about it (`listed`), without
  judging it.
- **6 come from the EOSC EU Node Resource Hub** ([Data Sources](https://open-science-cloud.ec.europa.eu/resources/datasources),
  read through its public catalogue API on 4 November 2026). They are EGI's,
  Italy's and PaNOSC's Service Catalogues, and Poland's Most Wiedzy, RepOD and
  ROHub. The Hub has no status column, so these entries have no `listed`
  field; each note gives the Hub record PID and where the Hub's declared URL
  was corrected (EGI declares the host root, which answers 404; RepOD
  declares `?verb=Identify`).

Each endpoint was sent one request: the sheet entries on 23 October 2026, the
Hub entries on 4 November 2026. All answered except the two Italian IRIS
OAI-PMH servers, which timed out at 20 s on 23 October. An answer shows only
that the endpoint is up, nothing about compliance. No check exists yet.

| Node | Service Catalogue | Research Product Catalogue(s) |
|---|---|---|
| BBMRI-ERIC | `eosc-catalogue.bbmri-eric.eu/services` | `eosc-catalogue.bbmri-eric.eu/oai` |
| CERN | | CERN Open Data (`opendata.cern/oai2d`) |
| Czechia | | National Metadata Directory (`test1.nma.du.cesnet.cz/oai2d`) |
| Data Terra | `services.earth-data.eu/services` | `resources.earth-data.eu/oai` |
| DTO | `gcat.d4science.org/.../EOSC-Node-DTO/services` | Zenodo community (`zenodo.org/oai2d`, set to be identified) |
| EGI | `egi-eosc-catalogue.dyn.cloud.e-infra.cz/services` (Hub) | |
| EUDAT | `portal.eudat.eu/api/services` | B2FIND (`b2find.eudat.eu/oai`) |
| Finland | `data.eosc.fi/v1/services` | |
| GÉANT | `geant-node-catalogue.geant.org/services` | |
| Italy | `gcat.d4science.org/.../EOSC-IT_Node/services` (Hub) | CNR IRIS, IRIS AperTO (UniTo) (`/oai/openaire4`) |
| PaNOSC | `pan-training.eu/service-catalogue/api/v3/services` (Hub) | RODARE (`rodare.hzdr.de/oai2d`) |
| Poland | | Most Wiedzy (`mostwiedzy.pl/en/oai-pmh`), RepOD (`repod.icm.edu.pl/oai`), ROHub (`api.rohub.org/api/oai2d/`) (all Hub) |
| Slovakia | `sc.eosc.sk/api/v1/services` | |

Not yet included: DTO's Blue-Cloud catalogue (no endpoint in the sheets),
catalogues listed as REJECTED, and the 13 data sources the Resource Hub
registers under the EOSC EU Node itself (Zenodo, PANGAEA, BASE and others),
which are not node catalogues. The Hub does not list BBMRI-ERIC's OAI-PMH
endpoint, which the sheets do.

```bash
uv sync
uv run catalogue-check version
uv run catalogue-check catalogues   # list and validate catalogues.yaml
uv run pytest -q
```
