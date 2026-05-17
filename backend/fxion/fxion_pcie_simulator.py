"""
FXION PCIe Simulator — pure-Python mirror of fxion_pcie_engine.cu
12 layers × 12 bridges · UCB1 (C=√2) · IQ2_XS primary · OBTERON9 QLOGIC entropy-epoch solver.

v2.1: now includes 3 MERGED fusion lanes (INT_K_ALL, IQ_XS_ALL, M_XSM_NL_HYBRID)
as additional UCB1 arms → 13 total candidates per bridge.

Functionally equivalent to the CUDA kernel:
  k1: ucb1_score_kernel
  k2: obteron9_qlogic_kernel (softmax + Shannon entropy)
  k3: update_reward_kernel
"""
import math
import time
import numpy as np
from dataclasses import dataclass
from fxion import qfusion


LAYERS = 12
BRIDGES = 12
LB = LAYERS * BRIDGES                # 144
UCB1_C = math.sqrt(2.0)
EPSILON = 0.0008
T_MAX = 2048


@dataclass
class Q:
    name: str
    accuracy: float
    vram_gb: float
    base_tps: float
    prior: float
    is_iq: bool
    is_fusion: bool = False
    boost: float = 1.0           # extra reward multiplier when this arm is pulled


# 10 base quants
BASE_QUANTS = [
    Q("Q2_K",   0.710, 1.20, 194.1, 0.00, False),
    Q("Q3_K",   0.820, 1.60, 178.6, 0.00, False),
    Q("Q4_K_M", 0.900, 2.10, 162.3, 0.05, False),
    Q("Q5_K_M", 0.940, 2.60, 151.8, 0.00, False),
    Q("Q6_K",   0.970, 3.10, 141.2, 0.00, False),
    Q("Q8_0",   0.991, 3.82, 128.4, 0.12, False),
    Q("IQ2_XS", 0.840, 0.95, 214.7, 0.06, True),    # ★ primary
    Q("IQ3_M",  0.910, 1.45, 188.9, 0.08, True),
    Q("IQ4_XS", 0.950, 1.85, 171.6, 0.10, True),
    Q("IQ4_NL", 0.975, 2.05, 166.2, 0.11, True),
]
IQ2_XS_INDEX = 6


def _build_fusion_arms():
    """Build merged fusion lanes as additional bandit arms."""
    merged = qfusion.all_merges()["merged_lanes"]
    arms = []
    for name in ("INT_K_ALL", "IQ_XS_ALL", "M_XSM_NL_HYBRID"):
        f = merged[name]
        is_iq = "IQ" in f["family_signature"]
        arms.append(Q(
            name=name,
            accuracy=f["fused_accuracy"],
            vram_gb=f["fused_vram_gb_mean"],
            base_tps=f["fused_tps_harmonic"],
            prior=f["summed_prior"],
            is_iq=is_iq,
            is_fusion=True,
            boost=f["boost_factor"],     # ← propagated multiplicative reward boost
        ))
    return arms


def _xorshift32_arr(state: np.ndarray) -> np.ndarray:
    s = state.astype(np.uint32)
    s ^= (s << np.uint32(13))
    s ^= (s >> np.uint32(17))
    s ^= (s << np.uint32(5))
    return s


def run(epochs: int = 256, capture_every: int = 0, include_fusion: bool = True,
        primary_override: str = None) -> dict:
    """Run OBTERON9 QLOGIC entropy-epoch solver with optional primary quant override."""
    epochs = max(8, min(epochs, T_MAX))
    quants = list(BASE_QUANTS)
    if include_fusion:
        quants.extend(_build_fusion_arms())
    QC = len(quants)
    name_to_idx = {q.name: i for i, q in enumerate(quants)}

    rewards = np.zeros((LB, QC), dtype=np.float32)
    counts  = np.zeros((LB, QC), dtype=np.int32)
    rng_state = np.array([((i * 0x9E3779B1) | 1) & 0xFFFFFFFF for i in range(LB)], dtype=np.uint32)

    acc   = np.array([q.accuracy  for q in quants], dtype=np.float32)
    vram  = np.array([q.vram_gb   for q in quants], dtype=np.float32)
    btps  = np.array([q.base_tps  for q in quants], dtype=np.float32)
    prior = np.array([q.prior     for q in quants], dtype=np.float32)
    is_iq = np.array([1.0 if q.is_iq else 0.0 for q in quants], dtype=np.float32)
    is_fusion = np.array([1.0 if q.is_fusion else 0.0 for q in quants], dtype=np.float32)
    boost_arr = np.array([q.boost for q in quants], dtype=np.float32)

    iq_eff_bonus = 0.08 * np.clip(1.0 - vram / 4.0, 0.0, 1.0) * is_iq
    iq2_xs_primary_bonus = np.zeros(QC, dtype=np.float32)
    if not primary_override:
        iq2_xs_primary_bonus[IQ2_XS_INDEX] = 0.10
    fusion_explore_bonus = 0.05 * is_fusion
    override_bonus = np.zeros(QC, dtype=np.float32)
    override_idx = -1
    if primary_override and primary_override in name_to_idx:
        override_idx = name_to_idx[primary_override]
        override_bonus[override_idx] = 0.18
    aug_prior = prior + iq_eff_bonus + iq2_xs_primary_bonus + fusion_explore_bonus + override_bonus

    W_ACC, W_SPD, W_VRAM = 0.30, 0.45, 0.25
    MIN_EPOCHS_FOR_CONVERGE = max(32, epochs // 4)

    t_start = time.time()
    trace = []
    total_h_history = []
    final_argmax = None
    final_entropy = None

    for t in range(1, epochs + 1):
        # K1: UCB1 score
        with np.errstate(divide="ignore", invalid="ignore"):
            n = counts.astype(np.float32)
            exploit = np.where(n > 0, rewards / np.maximum(n, 1), 0.0)
            explore = np.where(n > 0,
                               UCB1_C * np.sqrt(math.log(t + 1.0) / np.maximum(n, 1)),
                               1e6)
        scores = exploit + explore + aug_prior[None, :]

        # K2: OBTERON9 QLOGIC — softmax + Shannon entropy
        m = scores.max(axis=1, keepdims=True)
        e = np.exp(scores - m)
        psi = e / e.sum(axis=1, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            entropy_per_bridge = -np.sum(np.where(psi > 1e-9, psi * np.log2(psi + 1e-12), 0.0), axis=1)
        total_h = float(entropy_per_bridge.sum())
        total_h_history.append(total_h)

        argmax = scores.argmax(axis=1)

        # K3: update rewards
        rng_state = _xorshift32_arr(rng_state)
        jitter = ((rng_state.astype(np.int64) & 0xFFFF).astype(np.float32) - 32768.0) / 32768.0 * 0.03
        chosen_acc  = acc[argmax]
        chosen_vram = vram[argmax]
        chosen_btps = btps[argmax]
        chosen_boost = boost_arr[argmax]
        tps = chosen_btps * (1.0 + jitter)
        spd = np.minimum(tps / 220.0, 1.0)
        vram_eff = np.clip(1.0 - chosen_vram / 4.0, 0.0, 1.0)
        r = (W_ACC * chosen_acc + W_SPD * spd + W_VRAM * vram_eff) * chosen_boost
        r = np.where(argmax == IQ2_XS_INDEX, r * 1.18, r)
        r = np.where(argmax == 5, r * 1.05, r)
        if override_idx >= 0:
            r = np.where(argmax == override_idx, r * 1.20, r)

        np.add.at(rewards, (np.arange(LB), argmax), r)
        np.add.at(counts,  (np.arange(LB), argmax), 1)

        if capture_every and t % capture_every == 0:
            trace.append({
                "t": t,
                "total_entropy": round(total_h, 4),
                "mean_entropy":  round(total_h / LB, 4),
            })

        final_argmax = argmax
        final_entropy = entropy_per_bridge
        if t >= MIN_EPOCHS_FOR_CONVERGE and total_h < EPSILON * LB:
            break

    wall_ms = (time.time() - t_start) * 1000.0
    votes = np.bincount(final_argmax, minlength=QC).tolist()
    best_idx = int(np.argmax(votes))
    iq2_share = float(votes[IQ2_XS_INDEX] / LB)
    fusion_indices = [i for i, q in enumerate(quants) if q.is_fusion]
    fusion_share = sum(votes[i] for i in fusion_indices) / LB

    per_layer = []
    arg2d = final_argmax.reshape(LAYERS, BRIDGES)
    ent2d = final_entropy.reshape(LAYERS, BRIDGES)
    for L in range(LAYERS):
        bridge_votes = np.bincount(arg2d[L], minlength=QC).tolist()
        per_layer.append({
            "layer": L + 1,
            "backend": "CPU·AVX512" if L < 6 else "GPU·CUDA_FP16",
            "best": quants[int(np.argmax(bridge_votes))].name,
            "best_is_fusion": quants[int(np.argmax(bridge_votes))].is_fusion,
            "iq2_xs_count": int(bridge_votes[IQ2_XS_INDEX]),
            "fusion_count": sum(int(bridge_votes[i]) for i in fusion_indices),
            "entropy_mean": round(float(ent2d[L].mean()), 4),
            "votes": {quants[i].name: int(c) for i, c in enumerate(bridge_votes) if c},
        })

    return {
        "kernel": "FXION PCIe v2.1 (CUDA-mirror) · UCB1 + OBTERON9 QLOGIC + Fusion lanes",
        "topology": f"{LAYERS}L × {BRIDGES}B = {LB} bridges",
        "primary_quant": primary_override or "IQ2_XS",
        "primary_override_applied": bool(primary_override),
        "n_arms": QC,
        "n_base_arms": len(BASE_QUANTS),
        "n_fusion_arms": QC - len(BASE_QUANTS),
        "fusion_included": include_fusion,
        "ucb1_c": UCB1_C,
        "epsilon": EPSILON,
        "epochs_target": epochs,
        "epochs_converged": len(total_h_history),
        "converged": len(total_h_history) < epochs,
        "wall_ms": round(wall_ms, 3),
        "throughput_bridges_per_s": round(LB * len(total_h_history) / max(wall_ms / 1000, 1e-6), 0),
        "votes": {quants[i].name: int(v) for i, v in enumerate(votes) if v},
        "fusion_votes": {quants[i].name: int(votes[i]) for i in fusion_indices if votes[i]},
        "best_quant": quants[best_idx].name,
        "best_is_fusion": quants[best_idx].is_fusion,
        "iq2_xs_share": round(iq2_share, 4),
        "iq4_nl_share": round(float(votes[name_to_idx.get("IQ4_NL", 0)] / LB) if "IQ4_NL" in name_to_idx else 0.0, 4),
        "fusion_share": round(fusion_share, 4),
        "global_entropy_final": round(float(final_entropy.sum()), 4),
        "global_entropy_initial": round(total_h_history[0], 4) if total_h_history else None,
        "entropy_curve": [round(x, 4) for x in total_h_history[::max(1, len(total_h_history) // 64)]],
        "per_layer": per_layer,
        "trace_sample": trace[-8:],
        "build_command": "nvcc -arch=sm_52 -O3 fxion_pcie_engine.cu -o bin/fxion_pcie_v2",
    }
