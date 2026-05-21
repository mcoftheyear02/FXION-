"""
AI ENGINE QFX — INT4/Q8 Inference Coordinator
"""
import logging, time, json
from neural_core_qfx import NeuralCoreQFX
log = logging.getLogger("AI_ENGINE_QFX")

class AIEngineQFX:
    def __init__(self, quant: str = "Q8_0"):
        self.core    = NeuralCoreQFX(quant)
        self.quant   = quant
        self.session = 0
        log.info(f"AIEngineQFX ready | quant={quant}")

    def run(self, prompt: str) -> dict:
        self.session += 1
        t0     = time.time()
        result = self.core.generate(prompt, max_tokens=32)
        elapsed= time.time() - t0
        tps    = 32 / max(elapsed, 0.001)
        log.info(f"Session={self.session} tps={tps:.1f} quant={self.quant}")
        return {"session": self.session, "quant": self.quant,
                "result": result, "tps": round(tps,1), "elapsed_s": round(elapsed,3)}

if __name__ == "__main__":
    import logging as lg
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s — %(message)s")
    e = AIEngineQFX("Q8_0")
    print(json.dumps(e.run("What is quantization?"), indent=2))
