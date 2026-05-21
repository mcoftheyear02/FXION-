"""
NEURAL CORE -- CPU/GPU Neural Engine (FP32 baseline)
"""
import logging, time, random
log = logging.getLogger("NEURAL_CORE")

class NeuralCore:
    def __init__(self, device="cpu"):
        self.device = device
        self.layers = 32
        self.hidden = 4096
        log.info(f"NeuralCore init | device={device} | layers={self.layers} | hidden={self.hidden}")

    def forward(self, tokens: list) -> list:
        log.info(f"NeuralCore forward | input_len={len(tokens)}")
        time.sleep(random.uniform(0.01, 0.05))
        return [random.random() for _ in range(self.hidden)]

    def generate(self, prompt: str, max_tokens: int = 64) -> str:
        log.info(f"NeuralCore generate | max_tokens={max_tokens}")
        tokens = [ord(c) % 100 for c in prompt[:32]]
        for _ in range(max_tokens):
            out = self.forward(tokens)
            tokens.append(int(max(range(len(out)), key=lambda i: out[i])))
        return f"[NEURAL] generated {max_tokens} tokens"

if __name__ == "__main__":
    import logging as lg
    lg.basicConfig(level=lg.INFO, format="[%(asctime)s] %(levelname)s -- %(message)s")
    nc = NeuralCore()
    result = nc.generate("Hello world", max_tokens=10)
    print(result)
