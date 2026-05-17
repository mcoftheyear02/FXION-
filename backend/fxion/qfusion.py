"""
QUANT FUSION — Merge quant lanes into hybrid super-quants.

Defines 3 merge groups requested by FXION-ONYX:
  • INT_K_ALL       = Q2_K + Q3_K + Q4_K_M + Q5_K_M + Q6_K + Q8_0      (entire K family)
  • IQ_XS_ALL       = IQ2_XS + IQ4_XS                                   (XS variants)
  • M_XSM_NL_HYBRID = Q4_K_M + Q5_K_M + IQ4_XS + IQ4_NL                 (M-tier hybrid)

Fusion math:
  accuracy = accuracy-weighted mean of accuracies
  vram_gb  = mean (one lane chosen at inference time; max = peak)
  base_tps = harmonic mean (bottleneck-dominated)
  prior    = sum of priors (boost lane usage)
"""
import math
from typing import List, Dict


CATALOG = {
    "Q2_K":   {"family": "K",  "accuracy": 0.710, "vram_gb": 1.20, "base_tps": 194.1, "prior": 0.00},
    "Q3_K":   {"family": "K",  "accuracy": 0.820, "vram_gb": 1.60, "base_tps": 178.6, "prior": 0.00},
    "Q4_K_M": {"family": "K",  "accuracy": 0.900, "vram_gb": 2.10, "base_tps": 162.3, "prior": 0.05},
    "Q5_K_M": {"family": "K",  "accuracy": 0.940, "vram_gb": 2.60, "base_tps": 151.8, "prior": 0.00},
    "Q6_K":   {"family": "K",  "accuracy": 0.970, "vram_gb": 3.10, "base_tps": 141.2, "prior": 0.00},
    "Q8_0":   {"family": "K",  "accuracy": 0.991, "vram_gb": 3.82, "base_tps": 128.4, "prior": 0.12},
    "IQ2_XS": {"family": "IQ", "accuracy": 0.840, "vram_gb": 0.95, "base_tps": 214.7, "prior": 0.06},
    "IQ3_M":  {"family": "IQ", "accuracy": 0.910, "vram_gb": 1.45, "base_tps": 188.9, "prior": 0.08},
    "IQ4_XS": {"family": "IQ", "accuracy": 0.950, "vram_gb": 1.85, "base_tps": 171.6, "prior": 0.10},
    "IQ4_NL": {"family": "IQ", "accuracy": 0.975, "vram_gb": 2.05, "base_tps": 166.2, "prior": 0.11},
}

MERGES = {
    "INT_K_ALL":       ["Q2_K", "Q3_K", "Q4_K_M", "Q5_K_M", "Q6_K", "Q8_0"],
    "IQ_XS_ALL":       ["IQ2_XS", "IQ4_XS"],
    "M_XSM_NL_HYBRID": ["Q4_K_M", "Q5_K_M", "IQ4_XS", "IQ4_NL"],
}


def _harmonic_mean(xs: List[float]) -> float:
    xs = [x for x in xs if x > 0]
    if not xs:
        return 0.0
    return len(xs) / sum(1.0 / x for x in xs)


def merge_lane(name: str, members: List[str]) -> Dict:
    profs = [CATALOG[m] for m in members]
    accs  = [p["accuracy"] for p in profs]
    vrams = [p["vram_gb"]  for p in profs]
    tps   = [p["base_tps"] for p in profs]
    pri   = [p["prior"]    for p in profs]

    # accuracy-weighted mean accuracy
    w_acc = sum(a * a for a in accs) / max(sum(accs), 1e-9)
    return {
        "name": name,
        "members": members,
        "n_members": len(members),
        "fused_accuracy": round(w_acc, 4),
        "min_accuracy": round(min(accs), 4),
        "max_accuracy": round(max(accs), 4),
        "fused_vram_gb_mean": round(sum(vrams) / len(vrams), 3),
        "peak_vram_gb": round(max(vrams), 3),
        "total_vram_gb_all_loaded": round(sum(vrams), 3),
        "fused_tps_harmonic": round(_harmonic_mean(tps), 2),
        "peak_tps": round(max(tps), 2),
        "summed_prior": round(sum(pri), 4),
        "boost_factor": round(1.0 + 0.04 * len(members), 3),  # 4% per merged member
        "family_signature": "+".join(sorted({CATALOG[m]["family"] for m in members})),
    }


def all_merges() -> Dict:
    merged = {name: merge_lane(name, members) for name, members in MERGES.items()}
    # rank by fused score: 0.5*accuracy + 0.3*spd + 0.2*vram_eff
    ranked = []
    for name, m in merged.items():
        spd  = min(m["fused_tps_harmonic"] / 220.0, 1.0)
        veff = max(0.0, 1.0 - m["fused_vram_gb_mean"] / 4.0)
        score = 0.5 * m["fused_accuracy"] + 0.3 * spd + 0.2 * veff
        score *= m["boost_factor"]
        ranked.append({"name": name, "score": round(score, 4), "fused": m})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {
        "catalog_size": len(CATALOG),
        "merge_count": len(MERGES),
        "merged_lanes": merged,
        "ranked": ranked,
        "winner": ranked[0]["name"],
    }
