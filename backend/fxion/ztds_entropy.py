"""
ZTDS — Zero-Trust Dynamic Stream
Dynamic entropy stream cipher using XOR + algebraic mixing (affine over GF(2^8)).
Experimental: rotating algebraic key schedule seeded by elliptic-style scalar walk.
"""
import os
import math
import hashlib
from typing import List


GF_POLY = 0x11B  # AES irreducible polynomial


def gf_mul(a: int, b: int) -> int:
    r = 0
    for _ in range(8):
        if b & 1:
            r ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return r & 0xFF


def _derive_seed(key: str) -> int:
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) & 0xFFFFFFFFFFFFFFFF


def keystream(key: str, n: int) -> bytes:
    """Generate n bytes of dynamic-entropy keystream."""
    s = _derive_seed(key)
    a = (s & 0xFF) or 0x57
    b = ((s >> 8) & 0xFF) or 0x9D
    c = ((s >> 16) & 0xFF) or 0x3F
    out = bytearray(n)
    for i in range(n):
        # algebraic step: a' = a*c xor b ; b' = b*a xor c ; c' = c xor (a*b)
        na = gf_mul(a, c) ^ b
        nb = gf_mul(b, a) ^ c
        nc = c ^ gf_mul(a, b)
        a, b, c = na, nb, nc
        out[i] = a ^ b ^ c ^ ((i * 0x9E) & 0xFF)
    return bytes(out)


def encrypt(plaintext: bytes, key: str) -> bytes:
    ks = keystream(key, len(plaintext))
    return bytes(p ^ k for p, k in zip(plaintext, ks))


def decrypt(ciphertext: bytes, key: str) -> bytes:
    return encrypt(ciphertext, key)  # symmetric XOR stream


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for x in data:
        counts[x] += 1
    n = len(data)
    h = 0.0
    for c in counts:
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def encrypt_demo(message: str, key: str = "FXION-ONYX-ZTDS-2026") -> dict:
    pt = message.encode("utf-8")
    ct = encrypt(pt, key)
    rt = decrypt(ct, key).decode("utf-8")
    return {
        "algorithm": "ZTDS XOR + GF(2^8) algebraic stream",
        "key_id": hashlib.sha256(key.encode()).hexdigest()[:16],
        "plaintext": message,
        "ciphertext_hex": ct.hex(),
        "decrypted": rt,
        "match": rt == message,
        "plaintext_entropy_bits": round(shannon_entropy(pt), 4),
        "ciphertext_entropy_bits": round(shannon_entropy(ct), 4),
        "length": len(pt),
    }
