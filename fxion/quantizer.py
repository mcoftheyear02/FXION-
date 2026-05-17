"""
FXION QUANTIZER -- Q8/Q4 Weight Quantization Pipeline
Block-level quantization with per-block scale factors.
Optimized for GTX 970: block_size=32, INT8 primary, INT4 turbo.
"""
import math, logging
import numpy as np

log = logging.getLogger("FXION.QUANTIZER")

BLOCK_SIZE = 32
Q8_SCALE = 127.0
Q4_SCALE = 7.0
Q2_SCALE = 1.0


class FXIONQuantizer:
    """
    GPU-optimized weight quantizer supporting Q8_0, Q4_K_M, and Q2_K formats.
    Mirrors the CUDA kernel logic in fxion_pcie_engine.cu.
    """

    def __init__(self, block_size: int = BLOCK_SIZE):
        self.block_size = block_size
        self.stats = {"q8_calls": 0, "q4_calls": 0, "q2_calls": 0, "total_weights": 0}
        log.info(f"FXIONQuantizer init | block_size={block_size}")

    # -- Q2 Quantization -------------------------------------------------------
    def quantize_q2(self, weights: np.ndarray) -> tuple:
        """Quantize float32 -> INT2 (stored as int8) with per-block scales."""
        N = len(weights)
        n_blocks = math.ceil(N / self.block_size)
        q2 = np.zeros(N, dtype=np.int8)
        scales = np.zeros(n_blocks, dtype=np.float32)

        for b in range(n_blocks):
            start = b * self.block_size
            end = min(start + self.block_size, N)
            block = weights[start:end]
            amax = np.max(np.abs(block))
            scale = amax / Q2_SCALE
            scales[b] = scale
            q2[start:end] = np.clip(
                np.round(block / max(scale, 1e-8)), -1, 1
            ).astype(np.int8)

        self.stats["q2_calls"] += 1
        self.stats["total_weights"] += N
        log.info(f"Q2 quantize: {N} weights -> {n_blocks} blocks | "
                 f"size={q2.nbytes + scales.nbytes}B")
        return q2, scales

    # -- Q8 Quantization -------------------------------------------------------

    def quantize_q8(self, weights: np.ndarray) -> tuple:
        """Quantize float32 -> INT8 with per-block scales (Q8_0 format)."""
        N = len(weights)
        n_blocks = math.ceil(N / self.block_size)
        q8 = np.zeros(N, dtype=np.int8)
        scales = np.zeros(n_blocks, dtype=np.float32)

        for b in range(n_blocks):
            start = b * self.block_size
            end = min(start + self.block_size, N)
            block = weights[start:end]
            amax = np.max(np.abs(block))
            scale = amax / Q8_SCALE
            scales[b] = scale
            q8[start:end] = np.clip(
                np.round(block / max(scale, 1e-8)), -127, 127
            ).astype(np.int8)

        self.stats["q8_calls"] += 1
        self.stats["total_weights"] += N
        log.info(f"Q8 quantize: {N} weights -> {n_blocks} blocks | "
                 f"size={q8.nbytes + scales.nbytes}B")
        return q8, scales

    # -- Q8 Dequantization -----------------------------------------------------
    def dequantize_q8(self, q8: np.ndarray, scales: np.ndarray) -> np.ndarray:
        """Reconstruct float32 from INT8 + per-block scales."""
        N = len(q8)
        n_blocks = len(scales)
        out = np.zeros(N, dtype=np.float32)

        for b in range(n_blocks):
            start = b * self.block_size
            end = min(start + self.block_size, N)
            out[start:end] = q8[start:end].astype(np.float32) * scales[b]

        return out

    # -- Q4 Quantization -------------------------------------------------------
    def quantize_q4(self, weights: np.ndarray) -> tuple:
        """Quantize float32 -> INT4 (stored as int8) with per-block scales."""
        N = len(weights)
        n_blocks = math.ceil(N / self.block_size)
        q4 = np.zeros(N, dtype=np.int8)
        scales = np.zeros(n_blocks, dtype=np.float32)

        for b in range(n_blocks):
            start = b * self.block_size
            end = min(start + self.block_size, N)
            block = weights[start:end]
            amax = np.max(np.abs(block))
            scale = amax / Q4_SCALE
            scales[b] = scale
            q4[start:end] = np.clip(
                np.round(block / max(scale, 1e-8)), -7, 7
            ).astype(np.int8)

        self.stats["q4_calls"] += 1
        self.stats["total_weights"] += N
        log.info(f"Q4 quantize: {N} weights -> {n_blocks} blocks | "
                 f"size={q4.nbytes + scales.nbytes}B")
        return q4, scales

    # -- Error Metrics ----------------------------------------------------------
    def measure_error(self, original: np.ndarray, reconstructed: np.ndarray) -> dict:
        """Compute MAE, MSE, and max error between original and reconstructed."""
        diff = np.abs(original - reconstructed)
        return {
            "mae": float(np.mean(diff)),
            "mse": float(np.mean(diff ** 2)),
            "max_error": float(np.max(diff)),
            "snr_db": float(10 * np.log10(
                np.mean(original ** 2) / max(np.mean((original - reconstructed) ** 2), 1e-10)
            ))
        }

    # -- Full Pipeline ----------------------------------------------------------
    def pipeline(self, weights: np.ndarray, mode: str = "Q8_0") -> dict:
        """Run full quantize -> dequantize -> error measurement pipeline."""
        if mode in ("Q8_0", "Q8"):
            q, s = self.quantize_q8(weights)
            recon = self.dequantize_q8(q, s)
        elif mode in ("Q2_K", "Q2"):
            q, s = self.quantize_q2(weights)
            recon = self.dequantize_q8(q, s) # same deq logic
        else:
            q, s = self.quantize_q4(weights)
            recon = self.dequantize_q8(q, s)  # same deq logic, different scale


        error = self.measure_error(weights, recon)
        return {
            "mode": mode,
            "original_bytes": weights.nbytes,
            "quantized_bytes": q.nbytes + s.nbytes,
            "compression": round(weights.nbytes / (q.nbytes + s.nbytes), 2),
            "error": error
        }

    def report(self) -> dict:
        return self.stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s %(levelname)s -- %(message)s")
    import json
    np.random.seed(42)
    w = np.random.randn(4096).astype(np.float32) * 0.02

    fq = FXIONQuantizer()
    print("=== Q8 Pipeline ===")
    print(json.dumps(fq.pipeline(w, "Q8_0"), indent=2))
    print("\n=== Q4 Pipeline ===")
    print(json.dumps(fq.pipeline(w, "Q4_K_M"), indent=2))
