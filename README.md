# firai-data

The YAML knowledge base behind **FIRAI** (Forensic Investigation Reference
for AI): phases, evidence classes, techniques, forensic-readiness measures,
and GAP records, plus the schemas and scripts that validate and compile them.

## Layout

```
src/
  phases.yaml              # P01-P05
  evidence-classes.yaml    # EC01-EC07, with the asserted volatility ordering
  techniques/
    P01.yaml ... P05.yaml  # one file per phase; parents + sub-techniques
  readiness/
    readiness.yaml         # R0001-R0011
  gaps/
    gaps.yaml               # G0001-G0006
schemas/                   # JSON Schema for every record type
tools/
  compile.py                # src/ -> dist/FIRAI.yaml + dist/FIRAI.json
tests/
  test_validate.py          # pytest: schema + referential-integrity + CI rules
dist/                       # generated, gitignored — never commit this
```

## Working with the data

```bash
pip install -r requirements.txt

# validate everything (schema conformance, cross-references, claim-profile
# completeness on written pages, guard-string checks, count parity)
pytest

# compile src/ into a single distributable file
python tools/compile.py
# -> dist/FIRAI.yaml, dist/FIRAI.json
```

CI (`.github/workflows/ci.yml`) runs both on every push/PR. A broken
cross-reference or a schema violation fails the build.

## Adding or editing a technique

1. Edit the relevant `src/techniques/P0X.yaml` file (or add a new record).
2. Fill in `claim_profile` (does_establish / does_not_establish /
   alternative_propositions / corroboration_requirements /
   quality_controls / stop_conditions) for anything but the thinnest stub —
   `tests/test_validate.py` enforces this on flagship pages and will grow to
   cover more IDs as pages are written.
3. `pytest` locally before opening a PR.
4. Bump `maturity.base` only via the safer-grade rule (take the lower grade
   when ambiguous; the community disputes upward).

## ID scheme

`P##` phases · `EC##` evidence classes · `T####` techniques (first two
digits name the home phase) · `T####.###` sub-techniques · `G####` GAPs ·
`R####` forensic readiness measures. IDs are never reused; retirement uses
`status: {draft|active|deprecated|superseded|withdrawn}` plus `aliases`,
`supersedes`, `replaced_by`.

## License

Content: CC BY 4.0. Tooling (`tools/`, `tests/`, `schemas/`): MIT. See
`LICENSE-CONTENT.md`.
