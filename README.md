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

Every endpoint but Poland's comes from the production sheet
`production_env_node_services.xlsx` (shared in October 2026): its "Service
Catalogue registered" column (tab "Services") and its "Research Product
Catalogue registered" column (tab "Research product catalogues"). Where the
sheet comments on a catalogue ("Comments", "Evaluation / EOSC-A"), the entry
quotes it in `listed`, without judging it.

Poland's three research product catalogues (Most Wiedzy, RepOD, ROHub) are
not in the production sheet; they come from the EOSC EU Node Resource Hub's
[Data Sources](https://open-science-cloud.ec.europa.eu/resources/datasources),
read through its public catalogue API on 4 November 2026. The Hub has no
comment column, so they quote nothing; each note gives the Hub record PID.

Left out: two rows of the research product tab that are web pages, not OAI-PMH
endpoints (Finland's `metax.fairdata.fi`, Poland's `odis.ecudo.pl`).

| Node | Service Catalogue | Research Product Catalogue(s) |
|---|---|---|
| BBMRI-ERIC | `eosc-catalogue.bbmri-eric.eu/services` | `eosc-catalogue.bbmri-eric.eu/oai` |
| CERN | | CERN Open Data (`opendata.cern/oai2d`) |
| Czechia | | National Metadata Directory (shown as `nma.du.cesnet.cz/oai2d`, queried at `test1.nma.du.cesnet.cz/oai2d`) |
| Data Terra | `services.earth-data.eu/services` | `resources.earth-data.eu/oai` |
| DTO | `gcat.d4science.org/.../EOSC-Node-DTO/services` | Zenodo community (`zenodo.org/oai2d`, set to be identified) |
| EGI | `egi-eosc-catalogue.dyn.cloud.e-infra.cz/services` | |
| EUDAT | `portal.eudat.eu/api/services` | B2FIND (`b2find.eudat.eu/oai`) |
| Finland | `data.eosc.fi/v1/services` | |
| GÉANT | `geant-node-catalogue.geant.org/services` | |
| Italy | `gcat.d4science.org/.../EOSC-IT_Node/services` | CNR IRIS, IRIS AperTO (UniTo) (`/oai/openaire4`) |
| PaNOSC | `pan-training.eu/service-catalogue/api/v3/services` | RODARE (`rodare.hzdr.de/oai2d`) |
| Poland | | Most Wiedzy (`mostwiedzy.pl/en/oai-pmh`), RepOD (`repod.icm.edu.pl/oai`), ROHub (`api.rohub.org/api/oai2d/`) (Resource Hub) |
| Slovakia | `sc.eosc.sk/api/v1/services` | |

Czechia: the page shows the intended production address
`https://nma.du.cesnet.cz/oai2d`, but the probe queries
`https://test1.nma.du.cesnet.cz/oai2d`, the address the sheet lists. On
4 November 2026 the production address presented a generic certificate and
answered 404 (field `display_endpoint` and the entry's note).

## Results page

The per-catalogue results are published at
**https://marioreale.github.io/eosc-catalogues-test/**, rebuilt by the
`results page` workflow on every push to `main` (or by hand, through
*Run workflow*). Each run:

1. runs the test suite (`pytest`, results included in the page);
2. runs `catalogue-check report`, which, for each catalogue, evaluates the
   configuration checks entry by entry and sends one request to its endpoint
   (`GET` for a Service Catalogue, `?verb=Identify` for OAI-PMH), recording
   the HTTP status, the time taken and a few facts from the answer;
3. publishes `site/` (static HTML reading `results.json`) to GitHub Pages.

A card is green when the endpoint answered in the expected format, amber when
it answered but something deserves a look (for example an Identify `baseURL`
that differs from the endpoint queried) or timed out, and red when it did not
answer or a configuration check failed. None of this is a compliance verdict.

```bash
uv sync
uv run catalogue-check version
uv run catalogue-check catalogues   # list and validate catalogues.yaml
uv run catalogue-check report       # write site/results.json (add --no-probe for offline)
uv run pytest -q
```
