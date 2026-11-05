# Results

The same results as the [results page](https://marioreale.github.io/eosc-catalogues-test/), updated by the
`results page` workflow on every run.

**[Open the copy of the page in this directory](https://htmlpreview.github.io/?https://github.com/marioreale/eosc-catalogues-test/blob/main/results/index.html)**
(shown through HTML Preview, since GitHub displays HTML files as source).

- `index.html`: the whole results page in one self-contained file, with styles,
  script, data and logos inlined. It shows the same page when opened through the
  links above, from a clone, or after download (web fonts load when online).
  GitHub itself shows HTML files as source code, not as pages.
- `results.json`: the data of the run.
- `README.md`: this summary.

Generated 2026-11-05T22:13:26Z from commit `065b78d` ([CI run](https://github.com/marioreale/eosc-catalogues-test/actions/runs/42119523606)).

- Catalogues: 22 from 13 nodes
- Configuration checks passed: 122 of 122
- Endpoints that answered the probe: 22 of 22
- Tests: 19 passed, 0 failed, 0 skipped, of 19

| Node | Catalogue | Type | Checks | Probe | Notes |
|---|---|---|---|---|---|
| BBMRI-ERIC | [EOSC Node BBMRI-ERIC Service Catalogue](https://eosc-catalogue.bbmri-eric.eu/services) | Service | 5/5 | Up (HTTP 200 · 2.02 s) |  |
| EOSC Finland | [EOSC-FI Service Catalogue](https://data.eosc.fi/v1/services) | Service | 5/5 | Up (HTTP 200 · 1.76 s) |  |
| EOSC DTO (D4Science) | [European DTO Service Catalogue](https://gcat.d4science.org/gcat/ext/eosc/EOSC-Node-DTO/services) | Service | 5/5 | Up (HTTP 200 · 3.37 s) |  |
| EOSC Node Slovakia | [EOSC Slovakia - Service Catalogue](https://sc.eosc.sk/api/v1/services) | Service | 5/5 | Up (HTTP 200 · 0.71 s) |  |
| Data Terra | [Data Terra EOSC Node Service Catalogue](https://services.earth-data.eu/services) | Service | 5/5 | Up (HTTP 200 · 0.77 s) |  |
| EUDAT | [EUDAT Node Service Catalogue](https://portal.eudat.eu/api/services) | Service | 5/5 | Up (HTTP 200 · 0.75 s) |  |
| GÉANT | [GEANT Service Catalogue](https://geant-node-catalogue.geant.org/services) | Service | 5/5 | Up (HTTP 200 · 0.78 s) |  |
| EGI | [EGI Service Catalogue](https://egi-eosc-catalogue.dyn.cloud.e-infra.cz/services) | Service | 5/5 | Up (HTTP 200 · 1.97 s) |  |
| EOSC Node Italy | [EOSC Node \| Italy Service Catalogue](https://gcat.d4science.org/gcat/ext/eosc/EOSC-IT_Node/services) | Service | 5/5 | Up (HTTP 200 · 1.35 s) |  |
| PaNOSC | [PaNOSC Service Catalogue](https://pan-training.eu/service-catalogue/api/v3/services) | Service | 5/5 | Up (HTTP 200 · 0.7 s) |  |
| BBMRI-ERIC | [EOSC Node BBMRI-ERIC Data Set Catalogue](https://eosc-catalogue.bbmri-eric.eu/oai) | Research product | 6/6 | Up (HTTP 200 · 0.72 s) |  |
| CERN | [CERN Open Data Portal](https://opendata.cern/oai2d) | Research product | 6/6 | Up (HTTP 200 · 1.16 s) |  |
| EOSC Node Italy | [CNR IRIS](https://iris.cnr.it/oai/openaire4) | Research product | 6/6 | Up (HTTP 200 · 0.93 s) |  |
| EOSC Node Italy | [IRIS AperTO (Università di Torino)](https://iris.unito.it/oai/openaire4) | Research product | 6/6 | Up (HTTP 200 · 0.88 s) |  |
| Data Terra | [Data Terra research products](https://resources.earth-data.eu/oai) | Research product | 6/6 | Up (HTTP 200 · 0.6 s) |  |
| PaNOSC | [RODARE (Rossendorf Data Repository)](https://rodare.hzdr.de/oai2d) | Research product | 6/6 | Up (HTTP 200 · 0.77 s) |  |
| EUDAT | [B2FIND](https://b2find.eudat.eu/oai) | Research product | 6/6 | Up · note (HTTP 200 · 2.98 s) | Identify declares baseURL http://131.175.206.246/oai, not the endpoint queried |
| EOSC DTO (D4Science) | [EOSC Node \| EU DTO Zenodo Community](https://zenodo.org/oai2d) | Research product | 6/6 | Up (HTTP 200 · 0.51 s) |  |
| EOSC Node Czechia | [National Metadata Directory](https://nma.du.cesnet.cz/oai2d) | Research product | 6/6 | Up (HTTP 200 · 1.45 s) |  |
| EOSC Node Poland | [Most Wiedzy Open Research Data Catalog](https://mostwiedzy.pl/en/oai-pmh) | Research product | 6/6 | Up · note (HTTP 200 · 1.21 s) | Identify declares baseURL https://mostwiedzy.pl/en/oai-pmh/, not the endpoint queried |
| EOSC Node Poland | [RepOD Repository for Open Data](https://repod.icm.edu.pl/oai) | Research product | 6/6 | Up (HTTP 200 · 0.99 s) |  |
| EOSC Node Poland | [ROHub](https://api.rohub.org/api/oai2d/) | Research product | 6/6 | Up · note (HTTP 200 · 1.42 s) | Identify declares baseURL https://&lt;arguments.base.Str object at 0x7fe6316da090&gt;/api/oai2d/, not the endpoint queried |

A green probe only means the endpoint is up and speaks the expected format;
none of this is a compliance verdict.
