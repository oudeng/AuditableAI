from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Render VERA and CaST evidence without retraining or changing estimands."""
from pathlib import Path
import csv
import hashlib
import itertools
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from auditableai.plotting import apply_thesis_style


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


records = []
output = FIGURES
output.mkdir(parents=True, exist_ok=True)


def save(fig, name, kind, sources, details):
    files = []
    for extension in ("png", "svg"):
        path = output / f"{name}.{extension}"
        fig.savefig(path, dpi=400, bbox_inches="tight")
        files.append({"path": display_path(path), "sha256": sha(path)})
    plt.close(fig)
    records.append({
        "name": name, "kind": kind,
        "sources": [{"path": display_path(p), "sha256": sha(p)} for p in sources],
        "details": details, "outputs": files,
        "generator": display_path(Path(__file__)),
        "generator_sha256": sha(Path(__file__)),
    })


apply_thesis_style(font_scale=1.35)
palette = sns.color_palette("colorblind", 4)
summary_path = EVIDENCE / "papers/vera/t_final.json"
summary = json.loads(summary_path.read_text())
faith = summary["faithfulness"]
fig, ax = plt.subplots(figsize=(7.7, 2.8))
for y, name in enumerate(("MIMIC", "eICU")):
    item = faith[name]
    assert item["n_seeds"] == 15
    lo, hi = item["ci95_T"]
    ax.errorbar(item["T"], y, xerr=[[item["T"] - lo], [hi - item["T"]]],
                fmt="o", color=palette[0], markersize=7, capsize=4, linewidth=1.8)
    ax.text(.017, y, f"Holm p = {item['p_holm']:.4f}",
            ha="left", va="center", fontsize=10)
ax.axvline(0, color="#555555", ls="--", lw=1)
ax.set_yticks([0, 1], ["MIMIC (15 seeds)", "eICU (15 seeds)"])
ax.set_ylim(1.6, -.6)
ax.set_xlim(-.065, .065)
ax.set_xticks([-.06, -.04, -.02, 0])
ax.set_xlabel("Mean seed-level faithfulness difference: D − TAP₀")
ax.set_title("With-prior comparison: reported effects and pointwise 95% intervals",
             loc="left", fontsize=11, pad=12)
ax.grid(axis="x", alpha=.15)
sns.despine(ax=ax, left=True)
fig.tight_layout()
save(fig, "vera_faithfulness", "redraw of supplied summary estimates",
     [summary_path], {
         "values": faith, "inference_unit": "15 seed blocks per table",
         "multiplicity": "two-table primary Holm family; intervals unadjusted",
         "upstream_ablation_matrices_reconstructed": False,
     })

recovery_path = EVIDENCE / "papers/vera/fair_same_host_recovery_cells.csv"
cells = rows(recovery_path)
keyed = {(r["method"], int(r["seed"]), r["regime"]): float(r["auroc"]) for r in cells}
assert len(keyed) == len(cells)
seeds = sorted({int(r["seed"]) for r in cells})
regimes = sorted({r["regime"] for r in cells})
assert len(seeds) == 5 and len(regimes) == 3
deltas = np.array([[keyed["Permutation-on-SNI-fair-noOracle", s, g]
                    - keyed["SNI-D-fairhost", s, g] for g in regimes] for s in seeds])
medians = np.median(deltas, axis=1)
observed = float(medians.mean())
null = np.array([np.mean(medians * signs)
                 for signs in itertools.product((-1, 1), repeat=len(seeds))])
probability = float(np.mean(abs(null) >= abs(observed) - 1e-12))
rng = np.random.default_rng(20260831)
bootstrap = medians[rng.integers(0, len(seeds), (10000, len(seeds)))].mean(axis=1)
lo, hi = np.percentile(bootstrap, [2.5, 97.5])
published = summary["recovery"]["probe_vs_D_same_host_symmetric"]
assert abs(observed - published["T"]) < 5e-7
assert np.max(abs(np.array([lo, hi]) - published["ci95_T"])) < 5e-7
assert probability == published["p_exact"] == .0625
assert np.all(deltas > 0)
stats = {
    "T": observed, "ci95_seed_bootstrap": [float(lo), float(hi)],
    "p_exact_two_sided": probability, "p_floor": 2 / 2 ** len(seeds),
    "n_seeds": len(seeds), "regimes": regimes, "seeds": seeds,
    "deltas_by_seed_and_regime": deltas.tolist(),
    "seed_median_deltas": medians.tolist(),
    "bootstrap": {"draws": 10000, "rng_seed": 20260831},
    "positive_cells": int(np.sum(deltas > 0)),
    "scope": "Reaggregation of released AUROC cells, no model retraining.",
}
fig, ax = plt.subplots(figsize=(7.7, 4.4))
display = {"interaction_xor": "Interaction / XOR",
           "linear_gaussian": "Linear Gaussian", "nonlinear_mixed": "Nonlinear mixed"}
for j, (regime, marker) in enumerate(zip(regimes, ("o", "s", "^"))):
    ax.scatter(deltas[:, j], np.arange(5) + (j - 1) * .14, marker=marker,
               color=palette[j], s=40, label=display[regime], zorder=3)
ax.scatter(medians, np.arange(5), marker="D", s=38, color="#222222",
           label="Seed median", zorder=4)
ax.axhline(4.6, color="#AAAAAA", lw=.7)
ax.errorbar(observed, 5.4, xerr=[[observed - lo], [hi - observed]], fmt="D",
            color="#222222", capsize=4, markersize=7, lw=1.8)
ax.text(.265, 5.4, "Exact p = 0.0625\n5 seed blocks", va="center", fontsize=10)
ax.axvline(0, color="#555555", ls="--", lw=.9)
ax.set_yticks([0, 1, 2, 3, 4, 5.4],
              [f"Seed {s}" for s in seeds] + ["Mean of medians"])
ax.set_ylim(6.2, -.6)
ax.set_xlim(-.01, max(.37, float(deltas.max()) + .02))
ax.set_xlabel("Recovery AUROC difference: symmetric probe − D (same host)")
ax.set_title("Regimes are nested within seeds", loc="left", fontsize=12, pad=10)
ax.grid(axis="x", alpha=.15)
sns.despine(ax=ax, left=True)
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.20),
          ncol=2, frameon=False, fontsize=10)
fig.subplots_adjust(left=.23, right=.98, top=.90, bottom=.27)
save(fig, "vera_recovery", "independent reaggregation of supplied AUROC cells",
     [recovery_path, summary_path], stats)

snapshot = EVIDENCE / "papers/cast"
table_path = snapshot / "table3_main.csv"
freeze_path = snapshot / "final_system_freeze.csv"
table = {r["system"]: r for r in rows(table_path)}
frozen = {(r["protocol"], r["ontology"]): float(r["parent_hits10"])
          for r in rows(freeze_path)}
systems = [("dense", "Dense"), ("bm25_dense", "BM25 + dense"),
           ("cast3", "CaST, 3 signals"), ("cast5", "CaST, 5 signals")]
values = {ontology: [float(table[s][f"inductive_{ontology}"]) for s, _ in systems]
          for ontology in ("HPO", "DO", "GO")}
for ontology in values:
    assert abs(values[ontology][-1] - frozen["inductive", ontology]) <= .00005
fig, axes = plt.subplots(1, 3, figsize=(8.1, 3.2), sharey=True)
for ax, (ontology, entries) in zip(axes, values.items()):
    for y, value in enumerate(entries):
        color = palette[0] if y == 3 else "#78838A"
        ax.scatter(value, y, color=color, s=65 if y == 3 else 38,
                   marker="D" if y == 3 else "o", zorder=3)
        ax.text(value + .025, y, f"{value:.4f}", va="center", fontsize=10)
    ax.set_title(ontology, fontsize=12)
    ax.set_xlim(.30, .96)
    ax.set_xticks([.3, .5, .7, .9])
    ax.set_xlabel("Parent Hits@10")
    ax.grid(axis="x", alpha=.15)
    sns.despine(ax=ax, left=True)
axes[0].set_yticks(range(4), [label for _, label in systems])
axes[0].set_ylim(3.6, -.6)
fig.suptitle("Inductive protocol: source-reported mean performance",
             fontsize=12, y=1.02)
fig.tight_layout()
save(fig, "cast_inductive", "redraw of final source-reported aggregate results",
     [table_path, freeze_path], {
         "systems": systems, "values": values,
         "final_configuration_check": "cast5 agrees with freeze to four-decimal table precision",
         "uncertainty": "No error bars or new significance comparisons.",
         "inference": "No query-level outcomes or model runs regenerated.",
     })

(CHECKS/'ch06_ch07_figure_provenance.json').write_text(
    json.dumps(records, indent=2) + "\n")
(CHECKS/'ch06_ch07_recomputation.json').write_text(
    json.dumps(stats, indent=2) + "\n")
print("Generated three figures; recovery T = %.9f, exact p = %.4f." % (observed, probability))
