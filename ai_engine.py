"""
AI ENGINE -- FP32 Inference Coordinator
"""
import logging, time
from neural_core import NeuralCore
log = logging.getLogger("AI_ENGINE")

class AIEngine:
    def __init__(self):
        self.core    = NeuralCore()
        self.session = 0
        log.info("AIEngine ready")

    def run(self, prompt: str) -> dict:
        self.session += 1
        t0 = time.time()
        result = self.core.generate(prompt, max_tokens=32)
        elapsed = time.time() - t0
        log.info(f"Session={self.session} elapsed={elapsed:.3f}s")
        return {"session": self.session, "result": result, "elapsed_s": round(elapsed,3)}

if __name__ == "__main__":
    import logging as lg, json
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s -- %(message)s")
    e = AIEngine()
    print(json.dumps(e.run("What is AI?"), indent=2))
