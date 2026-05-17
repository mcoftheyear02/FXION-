"""
QINT LEVELS — Unified INT2 / INT4 / INT8 compression-decompression + speed bench.
Per-block (32) symmetric quant. Returns compression ratio, MAE, encode/decode tok/s.
"""
import numpy as np
import math
import time
from fxion.qint_int2 import quantize_int2, dequantize_int2

BLOCK = 32


def _q_levels(bits: int):
    # symmetric range [-max_int, max_int]
    max_int = (1 << (bits - 1)) - 1
    return max_int


def quantize_int(weights: np.ndarray, bits: int):
    w = np.asarray(weights, dtype=np.float32).flatten()
    N = len(w)
    n_blk = math.ceil(N / BLOCK)
    max_int = _q_levels(bits)
    q = np.zeros(N, dtype=np.int16 if bits > 8 else np.int8)
    scales = np.zeros(n_blk, dtype=np.float32)
    for b in range(n_blk):
        sl = slice(b * BLOCK, min((b + 1) * BLOCK, N))
        blk = w[sl]
        s = float(np.max(np.abs(blk))) / max_int if np.any(blk) else 1e-8
        scales[b] = max(s, 1e-8)
        q[sl] = np.clip(np.round(blk / scales[b]), -max_int, max_int).astype(q.dtype)
    return q, scales


def dequantize_int(q: np.ndarray, scales: np.ndarray):
    N = len(q)
    out = np.zeros(N, dtype=np.float32)
    n_blk = len(scales)
    for b in range(n_blk):
        sl = slice(b * BLOCK, min((b + 1) * BLOCK, N))
        out[sl] = q[sl].astype(np.float32) * scales[b]
    return out


def bench(level: str = "QINT8", size: int = 8192, seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(size).astype(np.float32) * 0.02

    t0 = time.time()
    if level == "QINT2":
        packed, scales, N = quantize_int2(w)
        encode_t = time.time() - t0
        comp_bytes = packed.nbytes + scales.nbytes
        t1 = time.time()
        deq = dequantize_int2(packed, scales, N)
        decode_t = time.time() - t1
        bits = 2
    elif level == "QINT4":
        q, scales = quantize_int(w, 4)
        # pack two int4 per byte
        q4 = q.astype(np.int8) & 0x0F
        if len(q4) % 2:
            q4 = np.concatenate([q4, np.zeros(1, dtype=np.int8)])
        packed = (q4[0::2] | (q4[1::2] << 4)).astype(np.uint8)
        encode_t = time.time() - t0
        comp_bytes = packed.nbytes + scales.nbytes
        t1 = time.time()
        # unpack
        lo = (packed & 0x0F).astype(np.int8)
        hi = ((packed >> 4) & 0x0F).astype(np.int8)
        lo[lo > 7] -= 16
        hi[hi > 7] -= 16
        unpacked = np.empty(len(packed) * 2, dtype=np.int8)
        unpacked[0::2] = lo
        unpacked[1::2] = hi
        unpacked = unpacked[: len(w)]
        deq = dequantize_int(unpacked, scales)
        decode_t = time.time() - t1
        bits = 4
    else:  # QINT8
        q, scales = quantize_int(w, 8)
        encode_t = time.time() - t0
        comp_bytes = q.nbytes + scales.nbytes
        t1 = time.time()
        deq = dequantize_int(q, scales)
        decode_t = time.time() - t1
        bits = 8

    mae = float(np.mean(np.abs(w - deq)))
    rmse = float(np.sqrt(np.mean((w - deq) ** 2)))
    orig = w.nbytes
    return {
        "level": level,
        "bits": bits,
        "n_weights": int(size),
        "original_bytes": int(orig),
        "compressed_bytes": int(comp_bytes),
        "compression_ratio": round(orig / max(comp_bytes, 1), 2),
        "encode_ms": round(encode_t * 1000, 3),
        "decode_ms": round(decode_t * 1000, 3),
        "encode_mtoks": round(size / max(encode_t, 1e-6) / 1e6, 2),
        "decode_mtoks": round(size / max(decode_t, 1e-6) / 1e6, 2),
        "mae": round(mae, 6),
        "rmse": round(rmse, 6),
        "estimated_accuracy": round(max(0.0, 1.0 - rmse * 6), 4),
    }


def bench_all(size: int = 8192) -> dict:
    return {lvl: bench(lvl, size) for lvl in ("QINT2", "QINT4", "QINT8")}
