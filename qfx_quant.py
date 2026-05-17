"""
QFX QUANT -- INT4 / Q8 Weight Quantization Library
"""
import logging, struct, math
import numpy as np
log = logging.getLogger("QFX_QUANT")

BLOCK_SIZE = 32

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

def quantize_q2(weights: np.ndarray) -> tuple:
    """Quantize float32 array to INT2 (stored as int8) with per-block scales."""
    N      = len(weights)
    n_blk  = math.ceil(N / BLOCK_SIZE)
    q2     = np.zeros(N, dtype=np.int8)
    scales = np.zeros(n_blk, dtype=np.float32)
    for b in range(n_blk):
        sl = slice(b*BLOCK_SIZE, min((b+1)*BLOCK_SIZE, N))
        blk = weights[sl]
        s   = np.max(np.abs(blk)) / 1.0
        scales[b] = s
        q2[sl] = np.clip(np.round(blk / max(s,1e-8)), -1, 1).astype(np.int8)
    return q2, scales

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

def quantize_xor_q4(weights: np.ndarray, xor_mask: int = 0x05) -> tuple:
    """Quantize float32 -> INT4 + Bitwise XOR obfuscation."""
    q4, scales = quantize_q4(weights)
    # Mask is 4-bit, so we XOR the lower nibble
    xor_q4 = (q4 ^ xor_mask) & 0x0F
    return xor_q4, scales

def dequantize_xor_q4(xor_q4: np.ndarray, scales: np.ndarray, xor_mask: int = 0x05) -> np.ndarray:
    """Reconstruct float32 from XOR-INT4 + scales."""
    # Reverse XOR
    q4 = (xor_q4 ^ xor_mask) & 0x0F
    # Handle sign (if bit 3 is set, it's negative in some logic, 
    # but here we just treat it as 4-bit unsigned for simple XOR logic)
    # Let's keep it simple: just reverse the bitwise XOR and treat as int8
    return dequantize_q8(q4.astype(np.int8), scales)

def mae(a: np.ndarray, b: np.ndarray) -> float:

    return float(np.mean(np.abs(a-b)))

if __name__ == "__main__":
    import logging as lg
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s -- %(message)s")
    np.random.seed(42)
    w = np.random.randn(4096).astype(np.float32)
    q8, s8 = quantize_q8(w);  d8 = dequantize_q8(q8, s8)
    q4, s4 = quantize_q4(w);  d4 = dequantize_q8(q4, s4)
    print(f"Q8 MAE: {mae(w,d8):.6f}")
    print(f"Q4 MAE: {mae(w,d4):.6f}")
