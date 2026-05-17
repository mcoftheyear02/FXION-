"""
HYPERLEARN EPOCH — XOR-on-Success learning loop with dual backend (AVX512 / Cortex A72).
Simulates an iterative training run where successful epochs trigger an XOR-mixing
genetic step on the weight vector, and the per-epoch throughput differs by backend.
"""
import math
import random
import numpy as np
import hashlib
import time


# Backend speed/precision profiles (synthetic, deterministic)
BACKENDS = {
    "AVX512": {
        "vector_width": 512,
        "fp16_tflops": 2.3,
        "int8_tops": 9.2,
        "base_epoch_ms": 3.4,
        "noise": 0.012,
        "label": "x86 · CPU layers 1-6",
    },
    "CORTEX_A72": {
        "vector_width": 128,
        "fp16_tflops": 0.31,
        "int8_tops": 1.25,
        "base_epoch_ms": 12.8,
        "noise": 0.022,
        "label": "ARMv8 · NEON · RK3399 / Pi4",
    },
}

SUCCESS_THRESHOLD = 0.72   # reward > threshold => epoch success
XOR_MIX_MASK = 0x5A         # bias mask applied during XOR mixing


def _quantize_int8(w: np.ndarray) -> np.ndarray:
    s = np.max(np.abs(w)) / 127.0
    return np.clip(np.round(w / max(s, 1e-8)), -127, 127).astype(np.int8), float(s)


def _xor_mix(q: np.ndarray, mask: int = XOR_MIX_MASK) -> np.ndarray:
    """Apply XOR mixing to int8 weights. Symmetric, deterministic."""
    return (q.astype(np.int16) ^ mask).clip(-127, 127).astype(np.int8)


def run(epochs: int = 30, backend: str = "AVX512", lr: float = 0.04, weight_dim: int = 512, seed: int = 42) -> dict:
    if backend not in BACKENDS:
        backend = "AVX512"
    cfg = BACKENDS[backend]
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(weight_dim).astype(np.float32) * 0.05
    target = rng.standard_normal(weight_dim).astype(np.float32) * 0.05

    trace = []
    success_count = 0
    xor_applied = 0
    t_start = time.time()
    best_reward = -1.0
    best_epoch = 0

    for e in range(epochs):
        t0 = time.time()
        # noisy gradient descent toward target
        grad = (w - target) + rng.standard_normal(weight_dim).astype(np.float32) * cfg["noise"]
        w = w - lr * grad
        # measure: reward = 1 - normalized MSE
        mse = float(np.mean((w - target) ** 2))
        reward = max(0.0, 1.0 - mse / 0.0025)  # 0.05^2 baseline
        reward = min(1.0, reward)
        success = reward > SUCCESS_THRESHOLD
        action = "—"
        if success:
            success_count += 1
            # XOR mix on int8 quantized weights (genetic perturbation on success)
            q8, scale = _quantize_int8(w)
            mixed = _xor_mix(q8)
            # decode back with damped influence (5%)
            w_mixed = mixed.astype(np.float32) * scale
            w = 0.95 * w + 0.05 * w_mixed
            xor_applied += 1
            action = "XOR-MIX"
        # simulate epoch time per backend
        sim_ms = cfg["base_epoch_ms"] * (1.0 + rng.standard_normal() * 0.05)
        elapsed_ms = max(0.1, sim_ms)
        if reward > best_reward:
            best_reward = reward
            best_epoch = e
        trace.append({
            "epoch": e,
            "reward": round(reward, 4),
            "mse": round(mse, 6),
            "success": success,
            "action": action,
            "elapsed_ms": round(elapsed_ms, 3),
        })

    total_real_s = time.time() - t_start
    total_sim_s = sum(t["elapsed_ms"] for t in trace) / 1000.0
    final_w = w
    fingerprint = hashlib.blake2b(final_w.tobytes(), digest_size=16).hexdigest()
    return {
        "module": "HyperLearn Epoch · XOR-on-Success",
        "backend": backend,
        "backend_label": cfg["label"],
        "backend_profile": {
            "vector_width": cfg["vector_width"],
            "fp16_tflops": cfg["fp16_tflops"],
            "int8_tops": cfg["int8_tops"],
            "base_epoch_ms": cfg["base_epoch_ms"],
        },
        "epochs": epochs,
        "weight_dim": weight_dim,
        "lr": lr,
        "success_threshold": SUCCESS_THRESHOLD,
        "xor_mask": hex(XOR_MIX_MASK),
        "successes": success_count,
        "success_rate": round(success_count / max(epochs, 1), 4),
        "xor_applied": xor_applied,
        "best_epoch": best_epoch,
        "best_reward": round(best_reward, 4),
        "final_reward": trace[-1]["reward"],
        "sim_total_ms": round(total_sim_s * 1000, 2),
        "wall_total_ms": round(total_real_s * 1000, 2),
        "throughput_epochs_per_s": round(epochs / max(total_sim_s, 1e-6), 2),
        "weight_fingerprint_blake2b_128": fingerprint,
        "trace": trace,
    }


def compare(epochs: int = 30, weight_dim: int = 512, seed: int = 42) -> dict:
    avx = run(epochs=epochs, backend="AVX512", weight_dim=weight_dim, seed=seed)
    arm = run(epochs=epochs, backend="CORTEX_A72", weight_dim=weight_dim, seed=seed)
    return {
        "avx512": avx,
        "cortex_a72": arm,
        "speedup_vs_arm": round(arm["sim_total_ms"] / max(avx["sim_total_ms"], 1e-6), 2),
        "delta_success_rate": round(avx["success_rate"] - arm["success_rate"], 4),
        "delta_best_reward": round(avx["best_reward"] - arm["best_reward"], 4),
    }
