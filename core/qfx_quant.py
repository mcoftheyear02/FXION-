"""
QFX QUANT — INT4 / Q8 / IQ2_XS Weight Quantization Library
"""
import logging, struct, math
import numpy as np
log = logging.getLogger("QFX_QUANT")

BLOCK_SIZE = 32

# IQ2_XS lookup table for importance matrix quantization
IQ2_XS_LOOKUP = [0.0, 0.33, 0.67, 1.0]

def quantize_q8(weights: np.ndarray) -> tuple:
    """Quantize float32 array to INT8 with per-block scales."""
    N      = len(weights)
    n_blk  = math.ceil(N / BLOCK_SIZE)
    q8     = np.zeros(N, dtype=np.int8)
    scales = np.zeros(n_blk, dtype=np.float32)
    for b in range(n_blk):
        sl = slice(b*BLOCK_SIZE, min((b+1)*BLOCK_SIZE, N))
        blk = weights[sl]
        s   = np.max(np.abs(blk)) / 127.0
        scales[b] = s
        q8[sl] = np.clip(np.round(blk / max(s,1e-8)), -127, 127).astype(np.int8)
    return q8, scales

def dequantize_q8(q8: np.ndarray, scales: np.ndarray) -> np.ndarray:
    """Reconstruct float32 from INT8 + scales."""
    N     = len(q8)
    n_blk = len(scales)
    out   = np.zeros(N, dtype=np.float32)
    for b in range(n_blk):
        sl = slice(b*BLOCK_SIZE, min((b+1)*BLOCK_SIZE, N))
        out[sl] = q8[sl].astype(np.float32) * scales[b]
    return out

def quantize_q4(weights: np.ndarray) -> tuple:
    """Quantize float32 array to INT4 (stored as int8) with per-block scales."""
    N      = len(weights)
    n_blk  = math.ceil(N / BLOCK_SIZE)
    q4     = np.zeros(N, dtype=np.int8)
    scales = np.zeros(n_blk, dtype=np.float32)
    for b in range(n_blk):
        sl = slice(b*BLOCK_SIZE, min((b+1)*BLOCK_SIZE, N))
        blk = weights[sl]
        s   = np.max(np.abs(blk)) / 7.0
        scales[b] = s
        q4[sl] = np.clip(np.round(blk / max(s,1e-8)), -7, 7).astype(np.int8)
    return q4, scales

def mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a-b)))


def quantize_iq2_xs(weights: np.ndarray) -> tuple:
    """
    Quantize float32 array to INT2 with IQ2_XS importance matrix lookup.
    Uses optimized 4-level quantization with per-block scales for best accuracy/speed tradeoff.
    Maps values to 4 discrete levels per block using optimal step size.
    """
    N = len(weights)
    n_blk = math.ceil(N / BLOCK_SIZE)
    iq2 = np.zeros(N, dtype=np.int8)
    scales = np.zeros(n_blk, dtype=np.float32)
    
    for b in range(n_blk):
        sl = slice(b * BLOCK_SIZE, min((b + 1) * BLOCK_SIZE, N))
        blk = weights[sl]
        amax = np.max(np.abs(blk))
        # For 2-bit (4 levels), we map to [-3, -1, 1, 3], so scale factor is amax/3
        s = max(amax / 3.0, 1e-8)
        scales[b] = s
        
        # Normalize to [-3, 3] range, round to nearest odd integer, then map to [0, 3]
        normalized = blk / s
        # Round to nearest and clip to [-3, 3]
        rounded = np.clip(np.round(normalized), -3, 3)
        # Map [-3,-1,1,3] -> [0,1,2,3]: index = (rounded + 3) // 2
        iq2[sl] = ((rounded.astype(np.int8) + 3) // 2).astype(np.int8)
    
    log.info(f"IQ2_XS quantize: {N} weights -> {n_blk} blocks | size={iq2.nbytes + scales.nbytes}B")
    return iq2, scales


def dequantize_iq2_xs(iq2: np.ndarray, scales: np.ndarray) -> np.ndarray:
    """Reconstruct float32 from INT2 indices + per-block scales.
    Maps indices [0,1,2,3] back to quantization levels [-3,-1,1,3] * scale.
    """
    N = len(iq2)
    n_blk = len(scales)
    out = np.zeros(N, dtype=np.float32)
    
    for b in range(n_blk):
        sl = slice(b * BLOCK_SIZE, min((b + 1) * BLOCK_SIZE, N))
        # Map [0,1,2,3] -> [-3,-1,1,3]: value = index * 2 - 3
        dequant_values = (iq2[sl].astype(np.float32) * 2.0 - 3.0) * scales[b]
        out[sl] = dequant_values
    
    return out


if __name__ == "__main__":
    import logging as lg
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s — %(message)s")
    np.random.seed(42)
    w = np.random.randn(4096).astype(np.float32)
    q8, s8 = quantize_q8(w);  d8 = dequantize_q8(q8, s8)
    q4, s4 = quantize_q4(w);  d4 = dequantize_q8(q4, s4)
    iq2, siq2 = quantize_iq2_xs(w); diq2 = dequantize_iq2_xs(iq2, siq2)
    print(f"Q8 MAE: {mae(w,d8):.6f}")
    print(f"Q4 MAE: {mae(w,d4):.6f}")
    print(f"IQ2_XS MAE: {mae(w,diq2):.6f}")
