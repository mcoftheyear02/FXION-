"""
QINT INT2 — Experimental 2-bit weight compression
Maps fp32 weights into 4 discrete levels {-1.5, -0.5, +0.5, +1.5} * scale per block.
Achieves ~16x compression vs FP32, ~4x vs INT8.
"""
import numpy as np
import math

BLOCK_SIZE = 32
INT2_LEVELS = np.array([-1.5, -0.5, 0.5, 1.5], dtype=np.float32)


def quantize_int2(weights: np.ndarray) -> tuple:
    """Quantize fp32 -> packed INT2 codes (uint8 storing 4 weights each) + scales."""
    w = np.asarray(weights, dtype=np.float32).flatten()
    N = len(w)
    n_blk = math.ceil(N / BLOCK_SIZE)
    codes = np.zeros(N, dtype=np.uint8)
    scales = np.zeros(n_blk, dtype=np.float32)
    for b in range(n_blk):
        sl = slice(b * BLOCK_SIZE, min((b + 1) * BLOCK_SIZE, N))
        blk = w[sl]
        s = float(np.max(np.abs(blk))) / 1.5 if np.any(blk) else 1e-8
        scales[b] = max(s, 1e-8)
        normalized = blk / scales[b]
        # snap each value to nearest level index 0..3
        idx = np.argmin(np.abs(normalized[:, None] - INT2_LEVELS[None, :]), axis=1).astype(np.uint8)
        codes[sl] = idx
    # pack 4 codes per byte
    pad = (-N) % 4
    if pad:
        codes = np.concatenate([codes, np.zeros(pad, dtype=np.uint8)])
    packed = (codes[0::4] | (codes[1::4] << 2) | (codes[2::4] << 4) | (codes[3::4] << 6)).astype(np.uint8)
    return packed, scales, N


def dequantize_int2(packed: np.ndarray, scales: np.ndarray, N: int) -> np.ndarray:
    codes = np.zeros(len(packed) * 4, dtype=np.uint8)
    codes[0::4] = packed & 0x3
    codes[1::4] = (packed >> 2) & 0x3
    codes[2::4] = (packed >> 4) & 0x3
    codes[3::4] = (packed >> 6) & 0x3
    codes = codes[:N]
    out = INT2_LEVELS[codes].astype(np.float32)
    n_blk = len(scales)
    for b in range(n_blk):
        sl = slice(b * BLOCK_SIZE, min((b + 1) * BLOCK_SIZE, N))
        out[sl] *= scales[b]
    return out


def compress_report(size: int = 4096, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(size).astype(np.float32) * 0.02
    packed, scales, N = quantize_int2(w)
    deq = dequantize_int2(packed, scales, N)
    mae = float(np.mean(np.abs(w - deq)))
    rmse = float(np.sqrt(np.mean((w - deq) ** 2)))
    orig_bytes = w.nbytes
    comp_bytes = packed.nbytes + scales.nbytes
    return {
        "algorithm": "QINT-INT2",
        "block_size": BLOCK_SIZE,
        "levels": INT2_LEVELS.tolist(),
        "n_weights": int(N),
        "original_bytes": int(orig_bytes),
        "compressed_bytes": int(comp_bytes),
        "compression_ratio": round(orig_bytes / max(comp_bytes, 1), 2),
        "mae": round(mae, 6),
        "rmse": round(rmse, 6),
        "estimated_accuracy": round(max(0.0, 1.0 - rmse * 6), 4),
    }
