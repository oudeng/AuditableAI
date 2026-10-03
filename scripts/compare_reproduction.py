"""Compare fresh public-data runs with the frozen aggregate reference evidence.

Counts, labels and selected settings must agree exactly. Numerical outputs use
an absolute tolerance of 1e-9 (relative tolerance zero). Runtime, provenance
identities, serialization and timestamps are intentionally not compared.
"""
import argparse
import json
import math
from numbers import Integral, Real

import pandas as pd

from auditableai.paths import CHECKS, EVIDENCE, JAPAN, WORK, prepare_outputs

ATOL = 1e-9


def compare(reference, observed):
    stats = {"numeric_values": 0, "max_absolute_difference": 0.0}

    def walk(a, b, path):
        if isinstance(a, dict):
            assert a.keys() == b.keys(), f"Keys differ: {path}"
            for key in a:
                walk(a[key], b[key], f"{path}/{key}")
        elif isinstance(a, list):
            assert len(a) == len(b), f"Length differs: {path}"
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}/{i}")
        elif isinstance(a, bool) or a is None:
            assert a == b, f"Value differs: {path}"
        elif isinstance(a, Real):
            assert math.isfinite(a) and math.isfinite(b), f"Nonfinite: {path}"
            difference = abs(a - b)
            stats["numeric_values"] += 1
            stats["max_absolute_difference"] = max(stats["max_absolute_difference"], difference)
            if isinstance(a, Integral):
                assert a == b, f"Count/index differs: {path}"
            else:
                assert difference <= ATOL, f"Numerical difference {difference}: {path}"
        else:
            assert a == b, f"Label differs: {path}"

    walk(reference, observed, "root")
    return stats


def read(path):
    if path.suffix == ".csv":
        return pd.read_csv(path).to_dict(orient="records")
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("application", choices=["japan", "nhanes"])
    task = parser.parse_args().application
    prepare_outputs()
    results = {}
    if task == "nhanes":
        ref = read(EVIDENCE / "phase4b/nhanes_formal_v1/summary.json")
        obs = read(WORK / "runs/nhanes_formal_v1/summary.json")
        for key in ["task", "protocol_sha256", "metrics", "seeds", "inference"]:
            results[key] = compare(ref[key], obs[key])
        assert [r["selected"] for r in ref["seeds"]] == [r["selected"] for r in obs["seeds"]]
        a = read(EVIDENCE / "phase4b/nhanes_formal_v1/audit_v1/summary.json")
        b = read(WORK / "runs/nhanes_formal_v1/audit_v1/summary.json")
        fields = ["arm", "family", "n", "invalid_truth", "rejected"]
        results["audit_counts"] = compare(
            [{k: r[k] for k in fields} for r in a["aggregates"]],
            [{k: r[k] for k in fields} for r in b["aggregates"]])
        verified = read(WORK / "runs/nhanes_verification_v1/verification.json")
        assert verified["all_passed"] and len(verified["checks"]) == 15
    else:
        refdir = EVIDENCE / "japan_health"
        for filename in ["metrics.csv", "paired_intervals.json", "selection.json", "spatial_selection.json"]:
            a, b = read(refdir / filename), read(JAPAN / "formal_v1" / filename)
            results[filename] = compare(a, b)
            if filename == "selection.json":
                assert {k: v["params"] for k, v in a.items()} == {k: v["params"] for k, v in b.items()}
            if filename == "spatial_selection.json":
                for region in a:
                    assert {k: v["params"] for k, v in a[region].items()} == {k: v["params"] for k, v in b[region].items()}
        a, b = read(refdir / "run_summary.json"), read(JAPAN / "formal_v1/run_summary.json")
        fields = ["training_strata", "test_strata", "test_prefecture_sex_years", "primary_metrics"]
        results["run_summary"] = compare({k: a[k] for k in fields}, {k: b[k] for k in fields})
        for filename in ["yearly_model_metrics.csv", "gate_yearly_decomposition.csv", "delta_gate_activity.csv", "diagnostic_summary.json"]:
            a, b = read(refdir / filename), read(JAPAN / "review1_v1" / filename)
            if filename.endswith(".json"):
                a.pop("sources", None)
                b.pop("sources", None)
            results[filename] = compare(a, b)
        verified = read(JAPAN / "formal_v1/verification.json")
        assert verified["normalized_numerator_denominator_pairs_verified"] == 5922
        assert len(verified["selected_model_replay"]) == 48
        assert verified["claims"] == 188
    report = {"application": task, "status": "PASS", "absolute_tolerance": ATOL,
              "relative_tolerance": 0, "selected_configurations": "exactly matched",
              "exclusions": ["timings", "timestamps", "source hashes after porting", "pickle bytes"],
              "checks": results}
    target = CHECKS / f"{task}_reference_comparison.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
