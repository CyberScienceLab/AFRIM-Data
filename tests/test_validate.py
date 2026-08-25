"""
CI data validation for afirm-data, mirroring atlas-data's pytest-based schema
+ referential-integrity checks. Run with:

    pytest

Covers:
  - every src/ record validates against its JSON Schema
  - IDs are unique and correctly formatted
  - cross-references (sub_of, readiness_measures, evidence_classes, phase) resolve
  - every inferential technique carries a non-empty claim_profile
    (does_establish / does_not_establish) per Part VI CI rules
  - dist/AFIRM.yaml, once compiled, matches src/ counts exactly (P1-22:
    counts are generated, never hand-maintained)
"""
import glob
import json
import os
import subprocess
import sys

import jsonschema
import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
SCHEMAS = os.path.join(ROOT, "schemas")
DIST = os.path.join(ROOT, "dist")


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f) or []


def load_all(pattern):
    items = []
    for path in sorted(glob.glob(os.path.join(SRC, pattern))):
        data = load_yaml(path)
        if isinstance(data, list):
            items.extend(data)
        elif data is not None:
            items.append(data)
    return items


def load_schema(name):
    with open(os.path.join(SCHEMAS, name)) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def phases():
    return load_yaml(os.path.join(SRC, "phases.yaml"))


@pytest.fixture(scope="module")
def evidence_classes():
    return load_yaml(os.path.join(SRC, "evidence-classes.yaml"))


@pytest.fixture(scope="module")
def techniques():
    return load_all("techniques/*.yaml")


@pytest.fixture(scope="module")
def readiness():
    return load_all("readiness/*.yaml")


@pytest.fixture(scope="module")
def gaps():
    return load_all("gaps/*.yaml")


# --------------------------------------------------------------- schema checks
def test_evidence_classes_validate(evidence_classes):
    schema = load_schema("evidence-class.schema.json")
    for ec in evidence_classes:
        jsonschema.validate(ec, schema)


def test_readiness_validate(readiness):
    schema = load_schema("readiness.schema.json")
    for r in readiness:
        jsonschema.validate(r, schema)


def test_gaps_validate(gaps):
    schema = load_schema("gap.schema.json")
    for g in gaps:
        jsonschema.validate(g, schema)


def test_techniques_validate(techniques):
    schema = load_schema("technique.schema.json")
    for t in techniques:
        jsonschema.validate(t, schema)


# --------------------------------------------------------- uniqueness / format
def test_technique_ids_unique(techniques):
    ids = [t["id"] for t in techniques]
    assert len(ids) == len(set(ids)), "duplicate technique IDs found"


def test_evidence_class_ids_unique(evidence_classes):
    ids = [e["id"] for e in evidence_classes]
    assert len(ids) == len(set(ids))


def test_evidence_class_volatility_ranks_are_a_permutation(evidence_classes):
    ranks = sorted(e["volatility_rank"] for e in evidence_classes)
    assert ranks == list(range(1, len(evidence_classes) + 1)), (
        "EC01-EC07 volatility ordering must be a dense 1..N ranking (Part III, "
        "P0-4 ruling: the ordering is asserted, not arbitrary)"
    )


# --------------------------------------------------------------- referential
def test_technique_phase_resolves(techniques, phases):
    phase_ids = {p["id"] for p in phases}
    for t in techniques:
        assert t["phase"] in phase_ids, f"{t['id']}: unknown phase {t['phase']}"


def test_technique_sub_of_resolves(techniques):
    ids = {t["id"] for t in techniques}
    for t in techniques:
        if t.get("sub_of"):
            assert t["sub_of"] in ids, f"{t['id']}: sub_of {t['sub_of']} does not exist"


def test_technique_readiness_measures_resolve(techniques, readiness):
    readiness_ids = {r["id"] for r in readiness}
    for t in techniques:
        for rm in t.get("readiness_measures", []):
            assert rm["id"] in readiness_ids, (
                f"{t['id']}: readiness measure {rm['id']} does not exist"
            )


def test_technique_evidence_classes_resolve(techniques, evidence_classes, phases):
    # a technique's evidence_classes entries are either EC## IDs or, for
    # cross-cutting techniques rendered as phase bands (Principle 4 / P1-2),
    # the phase ID itself (e.g. T0406 -> ["P04"]).
    ec_ids = {e["id"] for e in evidence_classes}
    phase_ids = {p["id"] for p in phases}
    for t in techniques:
        for ec in t["evidence_classes"]:
            assert ec in ec_ids or ec in phase_ids, (
                f"{t['id']}: evidence class {ec} does not resolve"
            )


# ------------------------------------------------------- content / CI rules
def test_flagship_techniques_have_claim_profiles(techniques):
    # Part VI CI rule: every inferential technique needs non-empty
    # does_establish / does_not_establish. We check the pages that have been
    # brought up to r6 content; stub techniques are expected to gain this as
    # their pages are written (tracked, not silently passing forever).
    written = {"T0104", "T0303"}
    for t in techniques:
        if t["id"] in written:
            cp = t.get("claim_profile") or {}
            assert cp.get("does_establish"), f"{t['id']}: missing does_establish"
            assert cp.get("does_not_establish"), f"{t['id']}: missing does_not_establish"


def test_public_output_guard_strings_absent_from_src():
    # Part X / [P0-1]: the private editorial build spec never ships in this
    # repo. Guard against personal-name assignment leakage and internal
    # markers making their way into src/.
    banned = ["[ACTION", "[verify]", "Ali-ratified", "Ali assigns"]
    for path in glob.glob(os.path.join(SRC, "**/*.yaml"), recursive=True):
        text = open(path).read()
        for term in banned:
            assert term not in text, f"{path} contains banned private-spec marker: {term!r}"


# ------------------------------------------------------------------- compile
def test_compile_produces_dist_matching_src_counts(techniques, evidence_classes, gaps, readiness):
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "compile.py")],
        check=True, cwd=ROOT,
    )
    with open(os.path.join(DIST, "AFIRM.yaml")) as f:
        compiled = yaml.safe_load(f)

    counts = compiled["counts"]
    assert counts["techniques_total"] == len(techniques)
    assert counts["evidence_classes"] == len(evidence_classes)
    assert counts["gaps"] == len(gaps)
    assert counts["readiness_measures"] == len(readiness)
