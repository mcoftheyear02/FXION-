"""
HARD COMPRESSION + XOR PREFETCH HASH CHAIN
Combines:
  1. RLE pre-pass (run-length encoding)
  2. XOR-rotate prefetch transform (key-derived rotating XOR window)
  3. zlib level=9 entropy coder
  4. BLAKE2b 256-bit hash chain over prefetched blocks (tamper detection)
"""
import zlib
import hashlib
import os
from typing import List


def _rle(data: bytes) -> bytes:
    if not data:
        return b""
    out = bytearray()
    prev = data[0]
    run = 1
    for b in data[1:]:
        if b == prev and run < 255:
            run += 1
        else:
            out.append(prev)
            out.append(run)
            prev = b
            run = 1
    out.append(prev)
    out.append(run)
    return bytes(out)


def _un_rle(data: bytes) -> bytes:
    out = bytearray()
    for i in range(0, len(data), 2):
        out.extend([data[i]] * data[i + 1])
    return bytes(out)


def _xor_prefetch(data: bytes, key: bytes, decode: bool = False) -> bytes:
    """Rotating XOR window of size 32 derived from key. Stream-symmetric."""
    win = hashlib.blake2b(key, digest_size=32).digest()
    out = bytearray(len(data))
    for i in range(len(data)):
        out[i] = data[i] ^ win[i % 32]
        if i and (i % 32) == 0:
            win = hashlib.blake2b(win + data[max(0, i - 32):i] if not decode else win + bytes(out[max(0, i - 32):i]),
                                  digest_size=32).digest()
    return bytes(out)


def hash_chain(data: bytes, block: int = 256) -> List[str]:
    chain = []
    h = hashlib.blake2b(b"FXION-HARD-PREFETCH", digest_size=32).digest()
    for i in range(0, len(data), block):
        h = hashlib.blake2b(h + data[i:i + block], digest_size=32).digest()
        chain.append(h.hex())
    return chain


def compress(data: bytes, key: bytes = b"FXION-HARD-KEY") -> dict:
    rle = _rle(data)
    xored = _xor_prefetch(rle, key, decode=False)
    deflated = zlib.compress(xored, level=9)
    chain = hash_chain(xored, block=256)
    return {
        "original_bytes": len(data),
        "rle_bytes": len(rle),
        "xored_bytes": len(xored),
        "compressed_bytes": len(deflated),
        "compression_ratio": round(len(data) / max(len(deflated), 1), 3),
        "hash_chain_blocks": len(chain),
        "hash_chain_root": chain[-1] if chain else None,
        "ciphertext_hex_preview": deflated[:32].hex(),
        "ciphertext": deflated,  # not serialized further in API layer
    }


def decompress(deflated: bytes, key: bytes = b"FXION-HARD-KEY") -> bytes:
    xored = zlib.decompress(deflated)
    rle = _xor_prefetch(xored, key, decode=True)
    return _un_rle(rle)


def roundtrip_demo(message: str = None) -> dict:
    if message is None:
        # generate a compressible-ish blob
        message = ("FXION-ONYX QUANTUM GENESIS PHANTOM SPLIT " * 64).strip()
    payload = message.encode("utf-8")
    rep = compress(payload)
    decoded = decompress(rep["ciphertext"])
    match = decoded == payload
    rep = {k: v for k, v in rep.items() if k != "ciphertext"}
    rep["roundtrip_match"] = match
    rep["sample_input"] = message[:80] + ("…" if len(message) > 80 else "")
    return rep
