"""
CO-TRAINING · AVX512 ↔ Cortex A72 with IQ2_XS / IQ4_XS / IQ4_NL quant slots.
Each peer runs a HyperLearn epoch loop; at sync intervals they exchange
XOR-mixed INT8 weight signatures (peer-to-peer genetic recombination).
Then PCIe CUDA solver is applied with IQ4_NL set as primary override.
"""
import hashlib
import numpy as np
import time
from fxion import hyperlearn
from fxion import fxion_pcie_simulator


# Quant profile per peer (informational; HyperLearn doesn't quantize, it
# tracks reward shapes per backend).
PEER_QUANT_MAP = {
    "AVX512":     {"primary": "IQ4_NL",  "secondary": "IQ4_XS"},   # high-accuracy on x86
    "CORTEX_A72": {"primary": "IQ2_XS",  "secondary": "IQ4_XS"},   # speed/edge on ARM
}


def _xor_mix_int8(a_int8: np.ndarray, b_int8: np.ndarray) -> np.ndarray:
    """XOR-mix two INT8 weight vectors (peer-to-peer recombination)."""
    return ((a_int8.astype(np.int16) ^ b_int8.astype(np.int16)) & 0x7F).astype(np.int8)


def _to_int8(w: np.ndarray) -> tuple:
    s = float(np.max(np.abs(w))) / 127.0 if np.any(w) else 1e-8
    return np.clip(np.round(w / max(s, 1e-8)), -127, 127).astype(np.int8), s


def run(epochs: int = 40, sync_every: int = 8, weight_dim: int = 256, seed: int = 42,
        apply_pcie: bool = True) -> dict:
    """
    Run co-training loop:
      • peer A = AVX512  (target IQ4_NL)
      • peer B = CORTEX_A72 (target IQ2_XS)
      • every `sync_every` epochs, peers exchange XOR-mixed INT8 weights.
    Then optionally apply the PCIe CUDA solver with IQ4_NL primary override.
    """
    epochs = max(8, min(epochs, 200))
    sync_every = max(2, min(sync_every, epochs))

    rng = np.random.default_rng(seed)
    target = rng.standard_normal(weight_dim).astype(np.float32) * 0.05
    w_avx = rng.standard_normal(weight_dim).astype(np.float32) * 0.05
    w_arm = rng.standard_normal(weight_dim).astype(np.float32) * 0.05

    avx_trace, arm_trace = [], []
    syncs = []
    successes = {"AVX512": 0, "CORTEX_A72": 0}
    xor_exchanges = 0

    t0 = time.time()
    for e in range(epochs):
        # AVX512 step (lower noise, higher lr)
        grad_avx = (w_avx - target) + rng.standard_normal(weight_dim).astype(np.float32) * 0.012
        w_avx -= 0.05 * grad_avx
        mse_avx = float(np.mean((w_avx - target) ** 2))
        r_avx = max(0.0, min(1.0, 1.0 - mse_avx / 0.0025))
        avx_trace.append({"epoch": e, "reward": round(r_avx, 4)})
        if r_avx > 0.72:
            successes["AVX512"] += 1

        # Cortex A72 step (higher noise, smaller lr — edge constraint)
        grad_arm = (w_arm - target) + rng.standard_normal(weight_dim).astype(np.float32) * 0.022
        w_arm -= 0.035 * grad_arm
        mse_arm = float(np.mean((w_arm - target) ** 2))
        r_arm = max(0.0, min(1.0, 1.0 - mse_arm / 0.0025))
        arm_trace.append({"epoch": e, "reward": round(r_arm, 4)})
        if r_arm > 0.72:
            successes["CORTEX_A72"] += 1

        # Sync via XOR-mix
        if (e + 1) % sync_every == 0 and e + 1 < epochs:
            avx_q, s_avx = _to_int8(w_avx)
            arm_q, s_arm = _to_int8(w_arm)
            mixed = _xor_mix_int8(avx_q, arm_q)
            mixed_fp = mixed.astype(np.float32) * ((s_avx + s_arm) * 0.5)
            # 8% of the mix is grafted into each peer
            w_avx = 0.92 * w_avx + 0.08 * mixed_fp
            w_arm = 0.92 * w_arm + 0.08 * mixed_fp
            xor_exchanges += 1
            syncs.append({
                "epoch": e + 1,
                "avx_reward": round(r_avx, 4),
                "arm_reward": round(r_arm, 4),
                "mix_fingerprint": hashlib.blake2b(mixed.tobytes(), digest_size=8).hexdigest(),
            })

    wall_ms = (time.time() - t0) * 1000.0
    avg_avx = sum(t["reward"] for t in avx_trace) / max(len(avx_trace), 1)
    avg_arm = sum(t["reward"] for t in arm_trace) / max(len(arm_trace), 1)
    final_avx = avx_trace[-1]["reward"]
    final_arm = arm_trace[-1]["reward"]
    convergence_gap = round(abs(final_avx - final_arm), 4)

    result = {
        "module": "Co-training AVX512 ↔ Cortex A72",
        "iq_quants": ["IQ2_XS", "IQ4_XS", "IQ4_NL"],
        "peer_quant_map": PEER_QUANT_MAP,
        "epochs": epochs,
        "sync_every": sync_every,
        "xor_exchanges": xor_exchanges,
        "weight_dim": weight_dim,
        "successes": successes,
        "avg_reward": {
            "AVX512": round(avg_avx, 4),
            "CORTEX_A72": round(avg_arm, 4),
        },
        "final_reward": {
            "AVX512": final_avx,
            "CORTEX_A72": final_arm,
        },
        "convergence_gap": convergence_gap,
        "convergence_coherent": convergence_gap < 0.05,
        "wall_ms": round(wall_ms, 3),
        "avx_trace": avx_trace,
        "arm_trace": arm_trace,
        "syncs": syncs,
        "winner_peer": "AVX512" if final_avx >= final_arm else "CORTEX_A72",
    }

    # Apply PCIe CUDA with IQ4_NL primary override
    if apply_pcie:
        pcie = fxion_pcie_simulator.run(
            epochs=128, capture_every=8, include_fusion=False,
            primary_override="IQ4_NL",
        )
        result["pcie_solver"] = {
            "primary_quant_override": "IQ4_NL",
            "best_quant": pcie["best_quant"],
            "iq2_xs_share": pcie["iq2_xs_share"],
            "iq4_nl_share": pcie.get("iq4_nl_share", 0.0),
            "votes": pcie["votes"],
            "global_entropy_final": pcie["global_entropy_final"],
            "wall_ms": pcie["wall_ms"],
            "topology": pcie["topology"],
        }
    return result
