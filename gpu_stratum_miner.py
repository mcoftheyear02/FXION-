import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BIN_DIR = ROOT / "bin"
BIN_DIR.mkdir(exist_ok=True)
BINARY = BIN_DIR / ("fxion_gpu_ai_miner.exe" if os.name == "nt" else "fxion_gpu_ai_miner")
SOURCE = ROOT / "fxion_gpu_ai_miner.cu"

class FXIONGPUMiner:
    def __init__(self):
        self.binary_path = BINARY
        self.source_path = SOURCE

    def has_nvcc(self):
        return shutil.which("nvcc") is not None

    def compile(self):
        if self.binary_path.exists():
            return True
        if not self.has_nvcc():
            return False
        cmd = ["nvcc", "-O3", "-arch=sm_52", str(self.source_path), "-o", str(self.binary_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print("CUDA compilation failed:")
            print(proc.stderr)
            return False
        return True

    def available(self):
        return self.compile()

    def mine_job(self, job_data, duration=1):
        if not self.available():
            return None

        job_id = job_data[0] if len(job_data) > 0 else "fxion_job"
        nbits = job_data[6] if len(job_data) > 6 else "1d00ffff"
        try:
            proc = subprocess.run(
                [str(self.binary_path), job_id, nbits, str(int(duration))],
                capture_output=True,
                text=True,
                timeout=int(duration) + 10,
            )
        except subprocess.TimeoutExpired:
            return None

        if proc.returncode != 0:
            print("GPU miner failed:", proc.stderr.strip())
            return None

        for line in proc.stdout.splitlines():
            if line.startswith("FOUND "):
                nonce = int(line.split()[1])
                return {
                    "nonce": hex(nonce),
                    "job_id": job_id,
                    "ntime": job_data[7] if len(job_data) > 7 else "00000000"
                }
        return None

if __name__ == "__main__":
    miner = FXIONGPUMiner()
    if not miner.available():
        print("GPU miner not available. Install CUDA nvcc and try again.")
    else:
        print("GPU miner compiled and ready.")
