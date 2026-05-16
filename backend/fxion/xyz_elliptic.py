"""
X/Y/Z Axial Elliptic Cybersecurity Layer
Tri-axial elliptic curve handshake over secp256k1-style short Weierstrass curve.
Generates ephemeral keypairs on three axes (X, Y, Z) and a shared coherence digest.
"""
import os
import hashlib
import secrets
from typing import Tuple


# secp256k1 parameters
P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A  = 0
B  = 7
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def inv_mod(a: int, m: int) -> int:
    return pow(a, -1, m)


def point_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        m = (3 * x1 * x1 + A) * inv_mod(2 * y1, P) % P
    else:
        m = (y2 - y1) * inv_mod((x2 - x1) % P, P) % P
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)


def scalar_mul(k: int, point) -> Tuple[int, int]:
    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result


G = (GX, GY)


def keypair() -> Tuple[int, Tuple[int, int]]:
    priv = secrets.randbelow(N - 1) + 1
    pub = scalar_mul(priv, G)
    return priv, pub


def axial_handshake() -> dict:
    """Run an X/Y/Z tri-axial ECDH handshake. Returns coherence digest."""
    axes = {}
    shared_secrets = []
    for axis in ("X", "Y", "Z"):
        a_priv, a_pub = keypair()
        b_priv, b_pub = keypair()
        a_shared = scalar_mul(a_priv, b_pub)
        b_shared = scalar_mul(b_priv, a_pub)
        ok = a_shared == b_shared
        secret_bytes = a_shared[0].to_bytes(32, "big")
        digest = hashlib.sha256(secret_bytes).hexdigest()
        axes[axis] = {
            "alice_pub_x": hex(a_pub[0])[:18] + "…",
            "bob_pub_x":   hex(b_pub[0])[:18] + "…",
            "shared_digest": digest[:32],
            "agree": ok,
        }
        shared_secrets.append(secret_bytes)
    coherence = hashlib.sha512(b"".join(shared_secrets)).hexdigest()
    return {
        "curve": "secp256k1 (X/Y/Z axial)",
        "axes": axes,
        "coherence_digest_sha512": coherence,
        "all_axes_agree": all(v["agree"] for v in axes.values()),
    }


def sign_payload(payload: str, priv: int = None) -> dict:
    if priv is None:
        priv, _ = keypair()
    z = int(hashlib.sha256(payload.encode()).hexdigest(), 16) % N
    k = secrets.randbelow(N - 1) + 1
    R = scalar_mul(k, G)
    r = R[0] % N
    s = (inv_mod(k, N) * (z + r * priv)) % N
    return {"r": hex(r), "s": hex(s), "hash": hex(z)}
