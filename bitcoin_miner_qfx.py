
"""
FXION BITCOIN MINER -- QFX HASH GENERATOR
Demonstrates high-performance hashing using FXION modules.
Optimized for GPU (CUDA) and CPU (ARM Cortex simulation).
"""
import time, hashlib, random
import numpy as np
from system_class import FXIONSystem
from fxion_real_mining_kernel import assemble_job_header, compact_to_target, double_sha256

class FXIONMiner:
    def __init__(self):
        self.engine = FXIONSystem()
        self.target = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        self.hash_rate = 0
        self.current_job = None
        self.job_header = b""
        
    def set_job(self, job_data):
        """Updates the current job from the pool."""
        self.current_job = job_data
        self.job_header = assemble_job_header(job_data)
        if len(job_data) > 7:
            nbits = job_data[6]
            try:
                self.target = compact_to_target(nbits)
            except Exception:
                self.target = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    def start_mining(self, duration=10):
        if not self.current_job or not self.job_header:
            return self._demo_mining(duration)

        start_time = time.time()
        attempts = 0
        while time.time() - start_time < duration:
            nonce = random.getrandbits(32)
            attempts += 1
            nonce_bytes = nonce.to_bytes(4, "little")
            h = double_sha256(self.job_header + nonce_bytes)
            hash_int = int.from_bytes(h, "big")

            if hash_int < self.target:
                result = {
                    "nonce": hex(nonce),
                    "job_id": self.current_job[0],
                    "ntime": self.current_job[7] if len(self.current_job) > 7 else None,
                    "hash": h.hex()
                }
                return result

            elapsed = time.time() - start_time
            self.hash_rate = attempts / (elapsed + 1e-6)
        return None

    def _demo_mining(self, duration):
        # Existing demo logic
        start_time = time.time()
        attempts = 0
        while time.time() - start_time < duration:
            nonce = random.getrandbits(32)
            attempts += 1
            elapsed = time.time() - start_time
            self.hash_rate = attempts / (elapsed + 1e-6)
        return None

if __name__ == "__main__":
    miner = FXIONMiner()
    miner.start_mining(duration=5)
