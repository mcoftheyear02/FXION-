"""
NEURAL CORE QFX -- INT4/Q8 Quantized Neural Engine
"""
import logging, time, random
import numpy as np
from qfx_quant import quantize_q8, dequantize_q8
log = logging.getLogger("NEURAL_CORE_QFX")

class NeuralCoreQFX:
    def __init__(self, quant: str = "Q8_0"):
        self.quant  = quant
        self.hidden = 4096
        self._init_weights()
        log.info(f"NeuralCoreQFX init | quant={quant}")

    def _init_weights(self):
        np.random.seed(0)
        w = np.random.randn(self.hidden).astype(np.float32) * 0.02
        self.q_weights, self.scales = quantize_q8(w)
        log.info(f"  Weights quantized: {len(w)} -> {self.q_weights.nbytes}B (Q8)")

    def forward(self, tokens: list) -> list:
        w_fp = dequantize_q8(self.q_weights, self.scales)
        out  = [float(w_fp[i % self.hidden] + random.gauss(0, 0.001))
                for i in range(self.hidden)]
        return out

    def generate(self, prompt: str, max_tokens: int = 64) -> str:
        tokens = [ord(c) % 100 for c in prompt[:32]]
        for _ in range(max_tokens):
            out = self.forward(tokens)
            tokens.append(int(max(range(len(out)), key=lambda i: out[i])))
        return f"[QFX-{self.quant}] generated {max_tokens} tokens"

if __name__ == "__main__":
    import logging as lg
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s -- %(message)s")
    nc = NeuralCoreQFX("Q8_0")
    print(nc.generate("test", max_tokens=8))
