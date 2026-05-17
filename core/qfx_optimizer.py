
"""
QFX OPTIMIZER — Q8 Augmented Quantization with UCB1 RL
INT4 / Q8 / Mixed-Precision adaptive selection engine
"""
import math, time, logging, random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from system_class import FXIONSystem

log = logging.getLogger("QFX_OPTIMIZER")

# Mirrored from Omnitech.IQQuant.psm1 so the Python optimizer uses the same
# quant set displayed by omnitech.ps1. PowerShell modules are not imported
# directly here; keep this table in sync with Omnitech.IQQuant.psm1.
QUANT_PROFILES = {
    "Q2_K":   {"family": "K",  "accuracy": 0.710, "vram_gb": 1.20, "base_tps": 194.1, "prior": 0.00},
    "Q3_K":   {"family": "K",  "accuracy": 0.820, "vram_gb": 1.60, "base_tps": 178.6, "prior": 0.00},
    "Q4_K_M": {"family": "K",  "accuracy": 0.900, "vram_gb": 2.10, "base_tps": 162.3, "prior": 0.05},
    "Q5_K_M": {"family": "K",  "accuracy": 0.940, "vram_gb": 2.60, "base_tps": 151.8, "prior": 0.00},
    "Q6_K":   {"family": "K",  "accuracy": 0.970, "vram_gb": 3.10, "base_tps": 141.2, "prior": 0.00},
    "Q8_0":   {"family": "K",  "accuracy": 0.991, "vram_gb": 3.82, "base_tps": 128.4, "prior": 0.15},
    "IQ2_XS": {"family": "IQ", "accuracy": 0.840, "vram_gb": 0.95, "base_tps": 214.7, "prior": 0.06},
    "IQ3_M":  {"family": "IQ", "accuracy": 0.910, "vram_gb": 1.45, "base_tps": 188.9, "prior": 0.08},
    "IQ4_XS": {"family": "IQ", "accuracy": 0.950, "vram_gb": 1.85, "base_tps": 171.6, "prior": 0.10},
    "IQ4_NL": {"family": "IQ", "accuracy": 0.975, "vram_gb": 2.05, "base_tps": 166.2, "prior": 0.11},
}
QUANTS = list(QUANT_PROFILES.keys())

# Q8 Augmented + IQ importance-matrix config
Q8_BOOST_FACTOR   = 1.15   # reward multiplier when Q8 selected
INT4_BOOST_FACTOR = 1.08   # reward multiplier when INT4 (Q4_K_M) selected
IQ_BOOST_FACTOR   = 1.10   # reward multiplier for IQ importance-matrix quants
ACCURACY_FLOOR    = 0.90   # K-quants below this are exploration-only
IQ_ACCURACY_FLOOR = 0.82   # IQ quants are allowed lower due to VRAM efficiency

ACCURACY = {q: p["accuracy"] for q, p in QUANT_PROFILES.items()}
VRAM_GB  = {q: p["vram_gb"]  for q, p in QUANT_PROFILES.items()}
BASE_TPS = {q: p["base_tps"] for q, p in QUANT_PROFILES.items()}
PRIORS   = {q: p["prior"]    for q, p in QUANT_PROFILES.items()}
FAMILY   = {q: p["family"]   for q, p in QUANT_PROFILES.items()}


class QFXOptimizer:
    def __init__(self, system=None):
        self.system  = system
        self.counts  = {q: 0   for q in QUANTS}
        self.rewards = {q: 0.0 for q in QUANTS}
        self.t       = 0
        self.log     = []
        log.info("QFXOptimizer init — Q8 Augmented + IQ importance-matrix UCB1 ready")

    # ── UCB1 select ───────────────────────────────────────
    def _select(self) -> str:
        self.t += 1
        for q in QUANTS:
            if self.counts[q] == 0:
                return q
        scores = {}
        for q in QUANTS:
            floor = IQ_ACCURACY_FLOOR if FAMILY[q] == "IQ" else ACCURACY_FLOOR
            if ACCURACY[q] < floor:
                continue
            exploit = self.rewards[q] / self.counts[q]
            explore = math.sqrt(2 * math.log(self.t) / self.counts[q])
            vram_efficiency = max(0.0, 1.0 - (VRAM_GB[q] / 4.0))
            iq_efficiency_bonus = 0.04 * vram_efficiency if FAMILY[q] == "IQ" else 0.0
            aug = PRIORS[q] + iq_efficiency_bonus
            scores[q] = exploit + explore + aug
        return max(scores, key=scores.__getitem__)

    # ── Reward function ───────────────────────────────────
    def _reward(self, quant: str, tps: float) -> float:
        acc  = ACCURACY[quant]
        spd  = min(tps / 200.0, 1.0)
        vram = 1.0 - (VRAM_GB[quant] / 4.0)   # GTX 970 = 4GB
        r    = 0.45*acc + 0.30*spd + 0.25*vram
        # Augmented multipliers
        if quant == "Q8_0":
            r *= Q8_BOOST_FACTOR
        elif quant == "Q4_K_M":
            r *= INT4_BOOST_FACTOR
        elif FAMILY[quant] == "IQ":
            r *= IQ_BOOST_FACTOR
        return r

    # ── Simulate inference ────────────────────────────────
    def _bench(self, quant: str) -> float:
        tps = BASE_TPS[quant] + random.gauss(0, 2.5)
        # If system has GPU, apply clock boost
        if self.system:
            gpu = self.system.gpu_info
            if gpu.get("available") and gpu.get("clock_mhz", 0) >= 1500:
                tps *= 1.08
        return max(tps, 10.0)

    # ── Public API ────────────────────────────────────────
    def optimize(self, rounds: int = 20):
        log.info(f"QFX optimize: {rounds} rounds | Q8_BOOST={Q8_BOOST_FACTOR} | IQ_BOOST={IQ_BOOST_FACTOR}")
        for r in range(rounds):
            q   = self._select()
            tps = self._bench(q)
            rew = self._reward(q, tps)
            self.counts[q]  += 1
            self.rewards[q] += rew
            entry = {"round": r, "quant": q, "tps": round(tps,1), "reward": round(rew,4)}
            self.log.append(entry)
            log.info(f"  r={r:03d}  {q:<10}  tps={tps:.1f}  rew={rew:.4f}")

    def best_quant(self) -> str:
        if not any(self.counts.values()):
            return "Q8_0"
        avg = {q: self.rewards[q]/max(self.counts[q],1) for q in QUANTS}
        return max(avg, key=avg.__getitem__)

    def report(self) -> dict:
        return {
            "best": self.best_quant(),
            "rounds": self.t,
            "stats": {
                q: {
                    "pulls":      self.counts[q],
                    "avg_reward": round(self.rewards[q]/max(self.counts[q],1), 4),
                    "accuracy":   ACCURACY[q],
                    "tps_base":   BASE_TPS[q],
                    "vram_gb":    VRAM_GB[q],
                    "family":     FAMILY[q],
                    "prior":      PRIORS[q],
                    "q8_boosted": q == "Q8_0",
                    "iq_variant": FAMILY[q] == "IQ"
                } for q in QUANTS
            }
        }

if __name__ == "__main__":
    import json, logging as lg
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s — %(message)s")
    opt = QFXOptimizer()
    opt.optimize(30)
    print(json.dumps(opt.report(), indent=2))
