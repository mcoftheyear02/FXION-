"""
Quantum Cryptographic Entropy
Combines OS CSPRNG + SHA3 sponge + Von Neumann debiasing for high-entropy bitstreams.
Produces statistical entropy reports (Shannon, chi-square, runs test).
"""
import os
import math
import hashlib
from collections import Counter


def quantum_bytes(n: int) -> bytes:
    """High-entropy bytes via OS RNG re-mixed with SHA3-512 sponge."""
    raw = os.urandom(n + 64)
    out = bytearray()
    h = hashlib.sha3_512()
    h.update(raw)
    buf = h.digest()
    i = 0
    while len(out) < n:
        if i >= len(buf):
            h = hashlib.sha3_512(buf + os.urandom(32))
            buf = h.digest()
            i = 0
        out.append(buf[i])
        i += 1
    return bytes(out[:n])


def von_neumann_debias(bits: list) -> list:
    """Classic Von Neumann debiasing: 00,11 discarded; 01->0, 10->1."""
    out = []
    for i in range(0, len(bits) - 1, 2):
        a, b = bits[i], bits[i + 1]
        if a != b:
            out.append(0 if (a, b) == (0, 1) else 1)
    return out


def shannon(data: bytes) -> float:
    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def chi_square_uniform(data: bytes) -> float:
    n = len(data)
    expected = n / 256.0
    counts = Counter(data)
    return sum(((counts.get(b, 0) - expected) ** 2) / expected for b in range(256))


def runs_test(bits: list) -> dict:
    if len(bits) < 2:
        return {"runs": 0, "expected": 0}
    runs = 1
    for i in range(1, len(bits)):
        if bits[i] != bits[i - 1]:
            runs += 1
    ones = sum(bits)
    n = len(bits)
    p = ones / n if n else 0
    expected = 2 * n * p * (1 - p)
    return {"runs": runs, "expected": round(expected, 2), "ones_ratio": round(p, 4)}


def report(size: int = 1024) -> dict:
    raw = quantum_bytes(size)
    bits = [(b >> i) & 1 for b in raw for i in range(8)]
    debiased = von_neumann_debias(bits)
    return {
        "algorithm": "OS-CSPRNG + SHA3-512 sponge + Von-Neumann debias",
        "bytes_generated": size,
        "sample_hex": raw[:32].hex(),
        "shannon_bits_per_byte": round(shannon(raw), 4),
        "chi_square": round(chi_square_uniform(raw), 2),
        "chi_square_dof": 255,
        "runs_test": runs_test(bits[:8192]),
        "debiased_bit_yield": round(len(debiased) / max(len(bits), 1), 4),
        "fingerprint_sha3_256": hashlib.sha3_256(raw).hexdigest(),
    }
