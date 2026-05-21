"""
FXION PCIe BRIDGE -- Host<->Device Transfer Manager
Manages PCIe data transfer simulation, VRAM allocation, and kernel dispatch.
"""
import os, time, logging, subprocess
from dataclasses import dataclass
from typing import Optional

log = logging.getLogger("FXION.PCIE")


@dataclass
class TransferStats:
    direction: str          # "H2D" or "D2H"
    bytes_transferred: int
    elapsed_ms: float
    bandwidth_gbps: float


class PCIeBridge:
    """
    PCIe Gen3 x16 bridge for GTX 970.
    Theoretical bandwidth: 15.75 GB/s (bidirectional).
    Manages host-device memory transfers and kernel execution.
    """

    PCIE_GEN3_X16_GBPS = 15.75  # theoretical max

    def __init__(self):
        self.transfers: list = []
        self.vram_allocated_mb: float = 0.0
        self.vram_limit_mb: float = 4096.0  # GTX 970
        self._kernel_binary = self._locate_kernel()
        log.info(f"PCIeBridge init | PCIe Gen3 x16 | VRAM limit: {self.vram_limit_mb}MB")

    def _locate_kernel(self) -> Optional[str]:
        root = os.environ.get("FXION_PATH",
                              os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(root, "bin", "fxion_gpu.exe")
        return path if os.path.isfile(path) else None

    # -- VRAM Allocation --------------------------------------------------------
    def alloc(self, size_mb: float) -> bool:
        if self.vram_allocated_mb + size_mb > self.vram_limit_mb:
            log.error(f"VRAM overflow: {self.vram_allocated_mb}+{size_mb} > {self.vram_limit_mb}MB")
            return False
        self.vram_allocated_mb += size_mb
        log.info(f"VRAM alloc +{size_mb}MB -> {self.vram_allocated_mb}/{self.vram_limit_mb}MB")
        return True

    def free(self, size_mb: float):
        self.vram_allocated_mb = max(0, self.vram_allocated_mb - size_mb)
        log.info(f"VRAM free -{size_mb}MB -> {self.vram_allocated_mb}/{self.vram_limit_mb}MB")

    def free_all(self):
        self.vram_allocated_mb = 0.0
        log.info("VRAM freed (all)")

    # -- Transfer Simulation ----------------------------------------------------
    def transfer_h2d(self, size_bytes: int) -> TransferStats:
        """Host -> Device transfer (PCIe Gen3 x16)."""
        # Realistic throughput ~12 GB/s effective
        effective_gbps = self.PCIE_GEN3_X16_GBPS * 0.76  # ~76% efficiency
        elapsed_ms = (size_bytes / (effective_gbps * 1e9)) * 1000.0
        stats = TransferStats("H2D", size_bytes, round(elapsed_ms, 3), round(effective_gbps, 2))
        self.transfers.append(stats)
        return stats

    def transfer_d2h(self, size_bytes: int) -> TransferStats:
        """Device -> Host transfer."""
        effective_gbps = self.PCIE_GEN3_X16_GBPS * 0.76
        elapsed_ms = (size_bytes / (effective_gbps * 1e9)) * 1000.0
        stats = TransferStats("D2H", size_bytes, round(elapsed_ms, 3), round(effective_gbps, 2))
        self.transfers.append(stats)
        return stats

    # -- Kernel Dispatch --------------------------------------------------------
    def dispatch_kernel(self) -> bool:
        """Launch the compiled FXION CUDA kernel binary."""
        if not self._kernel_binary:
            log.warning("Kernel binary not found -- run build first")
            return False
        try:
            log.info(f"Dispatching kernel: {self._kernel_binary}")
            proc = subprocess.Popen(
                [self._kernel_binary],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate(timeout=30)
            if proc.returncode == 0:
                log.info("Kernel execution complete")
                if stdout:
                    for line in stdout.decode().strip().split("\n"):
                        log.info(f"  [KERNEL] {line}")
                return True
            else:
                log.error(f"Kernel failed (rc={proc.returncode}): {stderr.decode()}")
                return False
        except subprocess.TimeoutExpired:
            proc.kill()
            log.error("Kernel timed out (30s)")
            return False
        except Exception as e:
            log.error(f"Kernel dispatch error: {e}")
            return False

    # -- Build ------------------------------------------------------------------
    def build(self, arch: str = "sm_52") -> bool:
        """Compile fxion_pcie_engine.cu -> bin/fxion_gpu.exe"""
        root = os.environ.get("FXION_PATH",
                              os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cu_path = os.path.join(root, "fxion_pcie_engine.cu")
        bin_dir = os.path.join(root, "bin")
        out_path = os.path.join(bin_dir, "fxion_gpu.exe")

        if not os.path.isfile(cu_path):
            log.error(f"CUDA source not found: {cu_path}")
            return False

        os.makedirs(bin_dir, exist_ok=True)

        cmd = f'nvcc -arch={arch} -O2 -o "{out_path}" "{cu_path}"'
        log.info(f"Building: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                log.info(f"Build success: {out_path}")
                self._kernel_binary = out_path
                return True
            else:
                log.error(f"Build failed: {result.stderr}")
                return False
        except Exception as e:
            log.error(f"Build error: {e}")
            return False

    # -- Status -----------------------------------------------------------------
    def status(self) -> dict:
        return {
            "pcie": "Gen3 x16",
            "bandwidth_gbps": self.PCIE_GEN3_X16_GBPS,
            "vram_allocated_mb": self.vram_allocated_mb,
            "vram_limit_mb": self.vram_limit_mb,
            "vram_free_mb": self.vram_limit_mb - self.vram_allocated_mb,
            "kernel_binary": self._kernel_binary or "NOT BUILT",
            "transfers": len(self.transfers)
        }


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s %(levelname)s -- %(message)s")
    bridge = PCIeBridge()
    bridge.alloc(3820)  # Q8_0 model
    t = bridge.transfer_h2d(3820 * 1024 * 1024)
    print(f"H2D: {t.bytes_transferred / 1e6:.1f}MB in {t.elapsed_ms:.3f}ms @ {t.bandwidth_gbps} GB/s")
    print(json.dumps(bridge.status(), indent=2))
