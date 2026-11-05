# Results

The same results as the [results page](https://marioreale.github.io/eosc-catalogues-test/). This directory holds a copy
of that page, updated by the `results page` workflow on every run: `index.html`,
its scripts, styles and logos, and `results.json`. GitHub shows the HTML as source;
to see the page from a clone, run `python3 -m http.server -d results` and open
<http://localhost:8000/> (the page reads `results.json`, which browsers do not
load from a file opened directly). The table below gives the same results.

Generated 2026-11-05T10:51:59Z from commit `38c8af9` ([CI run](https://github.com/marioreale/eosc-catalogues-test/actions/runs/42014173845)).

- Catalogues: 22 from 13 nodes
- Configuration checks passed: 122 of 122
- Endpoints that answered the probe: 22 of 22
- Tests: 19 passed, 0 failed, 0 skipped, of 19

| Node | Catalogue | Type | Checks | Probe | Notes |
|---|---|---|---|---|---|
| BBMRI-ERIC | [EOSC Node BBMRI-ERIC Service Catalogue](https://eosc-catalogue.bbmri-eric.eu/services) | Service | 5/5 | Up (HTTP 200 · 0.63 s) |  |
| EOSC Finland | [EOSC-FI Service Catalogue](https://data.eosc.fi/v1/services) | Service | 5/5 | Up (HTTP 200 · 0.97 s) |  |
| EOSC DTO (D4Science) | [European DTO Service Catalogue](https://gcat.d4science.org/gcat/ext/eosc/EOSC-Node-DTO/services) | Service | 5/5 | Up (HTTP 200 · 1.33 s) |  |
| EOSC Node Slovakia | [EOSC Slovakia - Service Catalogue](https://sc.eosc.sk/api/v1/services) | Service | 5/5 | Up (HTTP 200 · 0.46 s) |  |
| Data Terra | [Data Terra EOSC Node Service Catalogue](https://services.earth-data.eu/services) | Service | 5/5 | Up (HTTP 200 · 0.6 s) |  |
| EUDAT | [EUDAT Node Service Catalogue](https://portal.eudat.eu/api/services) | Service | 5/5 | Up (HTTP 200 · 0.58 s) |  |
| GÉANT | [GEANT Service Catalogue](https://geant-node-catalogue.geant.org/services) | Service | 5/5 | Up (HTTP 200 · 0.36 s) |  |
| EGI | [EGI Service Catalogue](https://egi-eosc-catalogue.dyn.cloud.e-infra.cz/services) | Service | 5/5 | Up (HTTP 200 · 1.27 s) |  |
| EOSC Node Italy | [EOSC Node \| Italy Service Catalogue](https://gcat.d4science.org/gcat/ext/eosc/EOSC-IT_Node/services) | Service | 5/5 | Up (HTTP 200 · 0.38 s) |  |
| PaNOSC | [PaNOSC Service Catalogue](https://pan-training.eu/service-catalogue/api/v3/services) | Service | 5/5 | Up (HTTP 200 · 0.54 s) |  |
| BBMRI-ERIC | [EOSC Node BBMRI-ERIC Data Set Catalogue](https://eosc-catalogue.bbmri-eric.eu/oai) | Research product | 6/6 | Up (HTTP 200 · 0.74 s) |  |
| CERN | [CERN Open Data Portal](https://opendata.cern/oai2d) | Research product | 6/6 | Up (HTTP 200 · 1.01 s) |  |
| EOSC Node Italy | [CNR IRIS](https://iris.cnr.it/oai/openaire4) | Research product | 6/6 | Up (HTTP 200 · 0.71 s) |  |
| EOSC Node Italy | [IRIS AperTO (Università di Torino)](https://iris.unito.it/oai/openaire4) | Research product | 6/6 | Up (HTTP 200 · 0.67 s) |  |
| Data Terra | [Data Terra research products](https://resources.earth-data.eu/oai) | Research product | 6/6 | Up (HTTP 200 · 0.6 s) |  |
| PaNOSC | [RODARE (Rossendorf Data Repository)](https://rodare.hzdr.de/oai2d) | Research product | 6/6 | Up (HTTP 200 · 0.77 s) |  |
| EUDAT | [B2FIND](https://b2find.eudat.eu/oai) | Research product | 6/6 | Up · note (HTTP 200 · 1.42 s) | Identify declares baseURL http://131.175.206.246/oai, not the endpoint queried |
| EOSC DTO (D4Science) | [EOSC Node \| EU DTO Zenodo Community](https://zenodo.org/oai2d) | Research product | 6/6 | Up (HTTP 200 · 0.33 s) |  |
| EOSC Node Czechia | [National Metadata Directory](https://nma.du.cesnet.cz/oai2d) | Research product | 6/6 | Up (HTTP 200 · 1.02 s) |  |
| EOSC Node Poland | [Most Wiedzy Open Research Data Catalog](https://mostwiedzy.pl/en/oai-pmh) | Research product | 6/6 | Up · note (HTTP 200 · 0.91 s) | Identify declares baseURL https://mostwiedzy.pl/en/oai-pmh/, not the endpoint queried |
| EOSC Node Poland | [RepOD Repository for Open Data](https://repod.icm.edu.pl/oai) | Research product | 6/6 | Up (HTTP 200 · 0.68 s) |  |
| EOSC Node Poland | [ROHub](https://api.rohub.org/api/oai2d/) | Research product | 6/6 | Up · note (HTTP 200 · 1.11 s) | Identify declares baseURL https://&lt;arguments.base.Str object at 0x7fe6316da090&gt;/api/oai2d/, not the endpoint queried |

A green probe only means the endpoint is up and speaks the expected format;
none of this is a compliance verdict.
