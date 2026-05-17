"""
FXION Real Mining Kernel Helpers
Provides a simplified block header miner for Stratum-style jobs.
"""
import hashlib


def double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def compact_to_target(nbits: str) -> int:
    if isinstance(nbits, str):
        nbits = nbits.strip()
    if nbits.startswith("0x"):
        nbits = nbits[2:]
    if len(nbits) != 8:
        raise ValueError("Invalid nbits length")

    exponent = int(nbits[0:2], 16)
    coefficient = int(nbits[2:], 16)
    return coefficient * (1 << (8 * (exponent - 3)))


def assemble_job_header(job_data):
    if not job_data or len(job_data) < 8:
        return b""
    job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime = job_data[:8]
    header = f"{job_id}|{prevhash}|{coinb1}|{coinb2}|{merkle_branch}|{version}|{nbits}|{ntime}".encode()
    return header


def mine_job(job_header: bytes, target: int, duration: float = 1.0):
    import time, random
    start_time = time.time()
    attempts = 0
    while time.time() - start_time < duration:
        nonce = random.getrandbits(32)
        nonce_bytes = nonce.to_bytes(4, "little")
        h = double_sha256(job_header + nonce_bytes)
        if int.from_bytes(h, "big") < target:
            return nonce, h.hex()
        attempts += 1
    return None, None
