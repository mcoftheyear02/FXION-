"""
ELLIPTIC SEISMOGRAPH WAVE — Lissajous-style elliptic oscillator + amplitude signature.
Generates a 2D elliptic waveform (x(t), y(t)) and emits a SHA3-256 signature of
the resulting wave envelope. Used as a tamper-evident motion fingerprint.
"""
import math
import hashlib
import numpy as np


def wave(a: float = 3.0, b: float = 2.0, delta: float = math.pi / 4, n: int = 256, noise: float = 0.02, seed: int = 11) -> dict:
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 2 * math.pi, n, dtype=np.float32)
    x = np.sin(a * t + delta) + rng.standard_normal(n).astype(np.float32) * noise
    y = np.sin(b * t) + rng.standard_normal(n).astype(np.float32) * noise
    env = np.sqrt(x * x + y * y)
    amp_min, amp_max = float(env.min()), float(env.max())
    energy = float((env ** 2).sum())
    # signature
    payload = x.tobytes() + y.tobytes()
    sig = hashlib.sha3_256(payload).hexdigest()
    # zero-crossings = pseudo-seismic events
    zc_x = int(np.sum(np.diff(np.signbit(x)).astype(int)))
    zc_y = int(np.sum(np.diff(np.signbit(y)).astype(int)))
    return {
        "algorithm": "Elliptic Lissajous Seismograph",
        "a": a, "b": b, "delta": round(delta, 4),
        "samples": n,
        "x": [round(float(v), 4) for v in x.tolist()],
        "y": [round(float(v), 4) for v in y.tolist()],
        "amplitude_min": round(amp_min, 4),
        "amplitude_max": round(amp_max, 4),
        "energy": round(energy, 4),
        "zero_crossings_x": zc_x,
        "zero_crossings_y": zc_y,
        "signature_sha3_256": sig,
    }
