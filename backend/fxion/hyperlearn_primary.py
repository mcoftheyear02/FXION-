"""
HYPERLEARN PRIMARY · multi-layer activation
Runs the HyperLearn epoch loop on each layer in [start..end] with a chosen
primary quant (default IQ2_XS). Each layer has 12 bridges, all training in
parallel with XOR-on-success genetic mixing.
"""
import time
import numpy as np
import hashlib
from fxion.qfusion import CATALOG


BRIDGES_PER_LAYER = 12
SUCCESS_THRESHOLD = 0.72
XOR_MASK = 0x5A


def _to_int8(w: np.ndarray) -> tuple:
    s = float(np.max(np.abs(w))) / 127.0 if np.any(w) else 1e-8
    return np.clip(np.round(w / max(s, 1e-8)), -127, 127).astype(np.int8), s


def _xor_mix(q8: np.ndarray, mask: int = XOR_MASK) -> np.ndarray:
    return ((q8.astype(np.int16) ^ mask).clip(-127, 127)).astype(np.int8)


def run_layer(layer_id: int, quant: str, epochs: int, weight_dim: int, seed: int) -> dict:
    """Run HyperLearn for one layer across its 12 bridges."""
    profile = CATALOG[quant]
    rng = np.random.default_rng(seed + layer_id * 101)

    # backend characteristics from PHANTOM_SPLIT: L1-6 CPU·AVX512, L7-12 GPU
    backend = "CPU·AVX512" if layer_id <= 6 else "GPU·CUDA_FP16"
    backend_noise = 0.012 if backend.startswith("CPU") else 0.008  # GPU slightly less noisy
    backend_lr_mul = 1.0 if backend.startswith("CPU") else 1.15

    # quant-specific bias: IQ2_XS gives slightly faster but noisier convergence
    quant_lr = 0.04 * (1.10 if profile["base_tps"] > 200 else 1.0) * backend_lr_mul
    quant_noise = backend_noise * (1.0 + 0.4 * (1.0 - profile["accuracy"]))

    target = rng.standard_normal(weight_dim).astype(np.float32) * 0.05
    bridges = [rng.standard_normal(weight_dim).astype(np.float32) * 0.05
               for _ in range(BRIDGES_PER_LAYER)]

    trace = []
    successes = [0] * BRIDGES_PER_LAYER
    xor_count = 0

    for e in range(epochs):
        per_bridge_reward = []
        for b in range(BRIDGES_PER_LAYER):
            w = bridges[b]
            grad = (w - target) + rng.standard_normal(weight_dim).astype(np.float32) * quant_noise
            w = w - quant_lr * grad
            mse = float(np.mean((w - target) ** 2))
            reward = max(0.0, min(1.0, 1.0 - mse / 0.0025))
            if reward > SUCCESS_THRESHOLD:
                successes[b] += 1
                # XOR-on-success: quantize INT8, XOR mask 0x5A, dampen 5%
                q, s = _to_int8(w)
                mixed = _xor_mix(q)
                w = 0.95 * w + 0.05 * (mixed.astype(np.float32) * s)
                xor_count += 1
            bridges[b] = w
            per_bridge_reward.append(round(reward, 4))
        avg_reward = sum(per_bridge_reward) / BRIDGES_PER_LAYER
        trace.append({
            "epoch": e,
            "avg_reward": round(avg_reward, 4),
            "best_bridge_reward": round(max(per_bridge_reward), 4),
        })

    # Final fingerprints
    final_fingerprints = []
    for b in range(BRIDGES_PER_LAYER):
        q, _ = _to_int8(bridges[b])
        final_fingerprints.append(hashlib.blake2b(q.tobytes(), digest_size=6).hexdigest())

    return {
        "layer": layer_id,
        "backend": backend,
        "quant": quant,
        "quant_accuracy": profile["accuracy"],
        "quant_base_tps": profile["base_tps"],
        "bridges": BRIDGES_PER_LAYER,
        "epochs": epochs,
        "lr": round(quant_lr, 4),
        "successes_per_bridge": successes,
        "total_successes": sum(successes),
        "success_rate": round(sum(successes) / (BRIDGES_PER_LAYER * epochs), 4),
        "xor_applied": xor_count,
        "final_avg_reward": trace[-1]["avg_reward"],
        "final_best_reward": trace[-1]["best_bridge_reward"],
        "trace": trace,
        "fingerprints": final_fingerprints,
    }


def run(start_layer: int = 6, end_layer: int = 12, quant: str = "IQ2_XS",
        epochs: int = 30, weight_dim: int = 128, seed: int = 42) -> dict:
    """Run HyperLearn primary across the requested layer range."""
    start_layer = max(1, min(start_layer, 12))
    end_layer = max(start_layer, min(end_layer, 12))
    if quant not in CATALOG:
        quant = "IQ2_XS"
    epochs = max(8, min(epochs, 200))

    t0 = time.time()
    layers = []
    for L in range(start_layer, end_layer + 1):
        layers.append(run_layer(L, quant, epochs, weight_dim, seed))
    wall_ms = (time.time() - t0) * 1000.0

    total_bridges = len(layers) * BRIDGES_PER_LAYER
    total_succ = sum(l["total_successes"] for l in layers)
    total_xor  = sum(l["xor_applied"] for l in layers)
    grand_avg  = sum(l["final_avg_reward"] for l in layers) / len(layers)
    best_layer = max(layers, key=lambda l: l["final_avg_reward"])
    cpu_layers = [l for l in layers if l["backend"].startswith("CPU")]
    gpu_layers = [l for l in layers if l["backend"].startswith("GPU")]

    return {
        "module": "HyperLearn PRIMARY · layer-active",
        "quant": quant,
        "start_layer": start_layer,
        "end_layer": end_layer,
        "layer_count": len(layers),
        "bridges_total": total_bridges,
        "epochs": epochs,
        "wall_ms": round(wall_ms, 2),
        "total_successes": total_succ,
        "xor_total": total_xor,
        "grand_success_rate": round(total_succ / (total_bridges * epochs), 4),
        "grand_avg_final_reward": round(grand_avg, 4),
        "best_layer": best_layer["layer"],
        "best_layer_reward": best_layer["final_avg_reward"],
        "cpu_layers": len(cpu_layers),
        "gpu_layers": len(gpu_layers),
        "cpu_avg_reward": round(sum(l["final_avg_reward"] for l in cpu_layers) / max(len(cpu_layers), 1), 4),
        "gpu_avg_reward": round(sum(l["final_avg_reward"] for l in gpu_layers) / max(len(gpu_layers), 1), 4),
        "layers": layers,
    }
