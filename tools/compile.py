#!/usr/bin/env python3
"""
Compile afirm-data's src/ YAML sources into a single distributable AFIRM.yaml
(and a JSON mirror for site consumption), the way ATLAS's tools/ compiles
tactics/techniques/mitigations/case-studies into dist/ATLAS.yaml.

Usage:
    python tools/compile.py

Writes:
    dist/AFIRM.yaml
    dist/AFIRM.json
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
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


def compute_counts(techniques, evidence_classes, gaps, readiness):
    parents = [t for t in techniques if not t.get("sub_of")]
    subs = [t for t in techniques if t.get("sub_of")]
    return {
        "techniques_total": len(techniques),
        "techniques_parent": len(parents),
        "techniques_sub": len(subs),
        "evidence_classes": len(evidence_classes),
        "gaps": len(gaps),
        "readiness_measures": len(readiness),
    }


def main():
    phases = load_yaml(os.path.join(SRC, "phases.yaml"))
    evidence_classes = load_yaml(os.path.join(SRC, "evidence-classes.yaml"))
    techniques = load_all("techniques/*.yaml")
    readiness = load_all("readiness/*.yaml")
    gaps = load_all("gaps/*.yaml")

    # -- basic referential checks (full validation lives in tests/, this is a
    #    fail-fast sanity gate so a broken compile never reaches dist/) --
    ec_ids = {e["id"] for e in evidence_classes}
    phase_ids = {p["id"] for p in phases}
    technique_ids = {t["id"] for t in techniques}
    readiness_ids = {r["id"] for r in readiness}
    errors = []

    for t in techniques:
        if t["phase"] not in phase_ids:
            errors.append(f"{t['id']}: unknown phase {t['phase']}")
        for ec in t.get("evidence_classes", []):
            if ec not in ec_ids and ec not in phase_ids:
                errors.append(f"{t['id']}: unknown evidence class {ec}")
        if t.get("sub_of") and t["sub_of"] not in technique_ids:
            errors.append(f"{t['id']}: sub_of references unknown technique {t['sub_of']}")
        for rm in t.get("readiness_measures", []):
            if rm["id"] not in readiness_ids:
                errors.append(f"{t['id']}: readiness_measures references unknown {rm['id']}")

    if errors:
        print("COMPILE FAILED - referential integrity errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    compiled = {
        "afirm_version": "0.1",
        "schema_version": "0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": compute_counts(techniques, evidence_classes, gaps, readiness),
        "phases": phases,
        "evidence_classes": evidence_classes,
        "techniques": techniques,
        "readiness_measures": readiness,
        "gaps": gaps,
    }

    os.makedirs(DIST, exist_ok=True)
    yaml_path = os.path.join(DIST, "AFIRM.yaml")
    json_path = os.path.join(DIST, "AFIRM.json")

    with open(yaml_path, "w") as f:
        yaml.dump(compiled, f, sort_keys=False, allow_unicode=True, width=100)
    with open(json_path, "w") as f:
        json.dump(compiled, f, indent=2, ensure_ascii=False)

    print(f"wrote {yaml_path}")
    print(f"wrote {json_path}")
    print(f"counts: {compiled['counts']}")


if __name__ == "__main__":
    main()
