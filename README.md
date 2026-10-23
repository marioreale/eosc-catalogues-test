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

Skeleton only: no catalogue is configured (`catalogues.yaml` is empty) and no
check exists yet.

```bash
uv sync
uv run catalogue-check version
uv run catalogue-check catalogues
uv run pytest -q
```
