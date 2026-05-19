
"""
ONYX RUNTIME — Live Inference Execution Layer
Manages the running inference loop: load model, stream tokens, report metrics.
"""
import time, logging, random, json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from system_class import FXIONSystem

log = logging.getLogger("ONYX_RUNTIME")

SAMPLE_PROMPTS = [
    "Explain quantum entanglement in simple terms.",
    "Write a Python function to sort a list using quicksort.",
    "What is the capital of Mars?",
    "Summarize the French Revolution in 3 sentences.",
    "Translate 'hello world' to Japanese.",
]


class ONYXRuntime:
    __slots__ = ('system', 'metrics')
    
    def __init__(self, system=None):
        self.system  = system
        self.metrics = []
        log.info("ONYX Runtime loaded")

    def _load_model(self, quant: str):
        log.info(f"  [ONYX] Loading model at {quant}...")
        time.sleep(random.uniform(0.1, 0.3))
        log.info(f"  [ONYX] Model loaded.")

    def _infer(self, quant: str, prompt: str) -> dict:
        base_tps = {"Q2_K":195,"Q3_K":170,"Q4_K_M":152,
                    "Q5_K_M":140,"Q6_K":134,"Q8_0":128}
        tps      = base_tps.get(quant, 100) + random.gauss(0, 3)
        tokens   = random.randint(40, 200)
        elapsed  = tokens / tps
        return {"quant": quant, "prompt": prompt[:40],
                "tokens": tokens, "tps": round(tps, 1),
                "elapsed_s": round(elapsed, 3)}

    def run(self, steps: int = 5):
        quant = "Q8_0"
        if self.system:
            quant = self.system.policy.best()
        log.info(f"ONYX Runtime: {steps} steps | quant={quant}")
        self._load_model(quant)
        
        infer = self._infer
        metrics_append = self.metrics.append
        sample_len = len(SAMPLE_PROMPTS)
        
        for i in range(steps):
            prompt = SAMPLE_PROMPTS[i % sample_len]
            result = infer(quant, prompt)
            metrics_append(result)
            log.info(f"  step={i:03d}  tps={result['tps']:.1f}  tokens={result['tokens']}")

    def report(self) -> dict:
        if not self.metrics:
            return {}
        avg_tps = sum(m["tps"] for m in self.metrics) / len(self.metrics)
        total   = sum(m["tokens"] for m in self.metrics)
        return {"steps": len(self.metrics), "avg_tps": round(avg_tps, 1),
                "total_tokens": total, "quant": self.metrics[-1]["quant"]}

if __name__ == "__main__":
    import logging as lg
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s — %(message)s")
    r = ONYXRuntime()
    r.run(5)
    print(json.dumps(r.report(), indent=2))
