
"""
NNOX SCHEDULER — Neural Workload Router
Routes inference jobs to GPU/CPU/QFX based on VRAM availability and quant policy.
"""
import logging, time, random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from system_class import FXIONSystem

log = logging.getLogger("NNOX_SCHEDULER")

ROUTE_GPU   = "GPU"
ROUTE_CPU   = "CPU"
ROUTE_HYBRID= "HYBRID"

VRAM_THRESHOLDS = {
    "Q2_K": 1.5, "Q3_K": 1.9, "Q4_K_M": 2.8,
    "Q5_K_M": 3.2, "Q6_K": 3.5, "Q8_0": 3.8
}


class NNOXScheduler:
    __slots__ = ('system', 'routes', 'job_id')
    
    def __init__(self, system=None):
        self.system   = system
        self.routes   = []
        self.job_id   = 0
        log.info("NNOX Scheduler initialized")

    def _get_free_vram_gb(self) -> float:
        if self.system:
            gpu = self.system.gpu_info
            if gpu.get("available"):
                return gpu.get("vram_free_mb", 0) / 1024.0
        return 0.0

    def _decide_route(self, quant: str) -> str:
        free = self._get_free_vram_gb()
        need = VRAM_THRESHOLDS.get(quant, 3.8)
        if free == 0.0:
            return ROUTE_CPU
        if free >= need:
            return ROUTE_GPU
        if free >= need * 0.5:
            return ROUTE_HYBRID
        return ROUTE_CPU

    def route(self, jobs: int = 5):
        log.info(f"NNOX routing {jobs} inference jobs")
        best_q = "Q8_0"
        if self.system:
            best_q = self.system.policy.best()

        decide = self._decide_route
        routes_append = self.routes.append
        
        for _ in range(jobs):
            self.job_id += 1
            dest = decide(best_q)
            lat  = round(random.uniform(12, 45) if dest == ROUTE_GPU else random.uniform(80, 200), 1)
            entry = {"job_id": self.job_id, "quant": best_q, "route": dest, "latency_ms": lat}
            routes_append(entry)
            log.info(f"  JOB#{self.job_id:04d}  quant={best_q}  route={dest}  latency={lat}ms")

    def summary(self) -> dict:
        gpu_jobs = sum(1 for r in self.routes if r["route"] == ROUTE_GPU)
        cpu_jobs = sum(1 for r in self.routes if r["route"] == ROUTE_CPU)
        hyb_jobs = sum(1 for r in self.routes if r["route"] == ROUTE_HYBRID)
        avg_lat  = sum(r["latency_ms"] for r in self.routes) / max(len(self.routes), 1)
        return {"total": len(self.routes), "gpu": gpu_jobs, "cpu": cpu_jobs,
                "hybrid": hyb_jobs, "avg_latency_ms": round(avg_lat, 1)}

if __name__ == "__main__":
    import logging as lg
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s — %(message)s")
    s = NNOXScheduler()
    s.route(10)
    import json
    print(json.dumps(s.summary(), indent=2))
