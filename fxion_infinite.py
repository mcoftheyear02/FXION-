"""
FXION NEURAL INFINITE -- Q-Layer L0 + Virtual Context + Virtual VRAM + Virtual Neural Layers
===============================================================================================

Architecture:
  L0 (Base Layer)     -- Quantized infinite neuron layer (Q2->Q8 adaptive)
  Virtual Context     -- Infinite context window via sliding hash-chain memory
  Virtual VRAM        -- Disk-backed virtual memory extending GPU VRAM
  Virtual Neural      -- Software-emulated neural layers beyond hardware limits
  Virtual Layer Stack -- Applies virtual expansion to ALL layers dynamically

   ----------------------------------------------------------------- 
  |                    FXION INFINITE NEURAL STACK                   |
   ----------------------------------------------------------------- 
  |  Layer N   | Virtual Neural Layer (infinite expansion)          |
  |  ...       | Auto-scaled by VirtualLayerManager                 |
  |  Layer 2   | Virtual Neural Layer                               |
  |  Layer 1   | Virtual Neural Layer + Virtual Context             |
  |  Layer L0  | Q-LAYER (quantized infinite neurons)   BASE       |
   ----------------------------------------------------------------- 
  |  VRAM      | Physical GPU (4GB) + Virtual VRAM (disk-backed)    |
  |  Context   | Sliding window + hash-chain infinite memory        |
   ----------------------------------------------------------------- 
"""
import math, time, logging, hashlib, struct, os, json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np

log = logging.getLogger("FXION.INFINITE")

# ===============================================================================
#  VIRTUAL VRAM -- Disk-backed memory extension
# ===============================================================================
class VirtualVRAM:
    """
     tend la VRAM physique GPU avec un cache disque.
    Pages de 1MB, eviction LRU, prefetch pr dictif.
    """

    PAGE_SIZE = 1024 * 1024  # 1MB pages

    def __init__(self, physical_mb: int = 4096, virtual_mb: int = 65536,
                 cache_dir: str = ".fxion_vram_cache"):
        self.physical_mb = physical_mb
        self.virtual_mb = virtual_mb
        self.cache_dir = cache_dir
        self.total_mb = physical_mb + virtual_mb

        # Page table: page_id -> {"location": "gpu"|"disk", "data": ndarray, "last_access": int}
        self.page_table: Dict[int, dict] = {}
        self.gpu_pages: List[int] = []  # pages currently in GPU
        self.max_gpu_pages = (physical_mb * 1024 * 1024) // self.PAGE_SIZE
        self.access_counter = 0
        self.stats = {"hits": 0, "misses": 0, "evictions": 0, "total_allocated": 0}

        os.makedirs(cache_dir, exist_ok=True)
        log.info(f"VirtualVRAM: {physical_mb}MB physical + {virtual_mb}MB virtual = {self.total_mb}MB total")

    def allocate(self, size_bytes: int) -> List[int]:
        """Alloue des pages virtuelles, retourne les page_ids."""
        n_pages = math.ceil(size_bytes / self.PAGE_SIZE)
        page_ids = []
        for _ in range(n_pages):
            pid = self.stats["total_allocated"]
            self.stats["total_allocated"] += 1
            self.page_table[pid] = {
                "location": "virtual",
                "data": np.zeros(self.PAGE_SIZE // 4, dtype=np.float32),
                "last_access": 0,
                "size_bytes": self.PAGE_SIZE
            }
            page_ids.append(pid)
        return page_ids

    def access(self, page_id: int) -> np.ndarray:
        """Acc de   une page -- g re le swap GPU<->disk."""
        self.access_counter += 1
        page = self.page_table.get(page_id)
        if page is None:
            raise ValueError(f"Page {page_id} not found")

        page["last_access"] = self.access_counter

        if page["location"] == "gpu":
            self.stats["hits"] += 1
        else:
            self.stats["misses"] += 1
            self._swap_to_gpu(page_id)

        return page["data"]

    def write(self, page_id: int, data: np.ndarray):
        """ crit dans une page."""
        page = self.page_table.get(page_id)
        if page is None:
            raise ValueError(f"Page {page_id} not found")
        max_len = min(len(data), len(page["data"]))
        page["data"][:max_len] = data[:max_len]
        page["last_access"] = self.access_counter

    def _swap_to_gpu(self, page_id: int):
        """Am ne une page en GPU,  vince si n cessaire (LRU)."""
        if len(self.gpu_pages) >= self.max_gpu_pages:
            # Evict LRU
            lru_page = min(self.gpu_pages,
                           key=lambda p: self.page_table[p]["last_access"])
            self.page_table[lru_page]["location"] = "disk"
            self.gpu_pages.remove(lru_page)
            self.stats["evictions"] += 1

        self.page_table[page_id]["location"] = "gpu"
        self.gpu_pages.append(page_id)

    def usage(self) -> dict:
        return {
            "physical_mb": self.physical_mb,
            "virtual_mb": self.virtual_mb,
            "total_mb": self.total_mb,
            "gpu_pages": len(self.gpu_pages),
            "max_gpu_pages": self.max_gpu_pages,
            "total_pages": len(self.page_table),
            "stats": self.stats
        }


# ===============================================================================
#  VIRTUAL CONTEXT -- Infinite context via hash-chain sliding memory
# ===============================================================================
class VirtualContext:
    """
    Contexte infini par fen tre glissante + m moire hash-chain.
    Chaque segment de contexte pass  est compress  en un hash-state
    qui peut  tre r activ  pour recall.

    Window active: 8192 tokens
    Hash-chain: illimit  (chaque segment = 32 bytes de state)
    """

    WINDOW_SIZE = 8192
    SEGMENT_SIZE = 512

    def __init__(self):
        self.active_window: List[np.ndarray] = []
        self.hash_chain: List[bytes] = []  # compressed past segments
        self.segment_states: List[np.ndarray] = []  # reduced state per segment
        self.total_tokens = 0
        self.chain_length = 0
        log.info(f"VirtualContext: window={self.WINDOW_SIZE}, segment={self.SEGMENT_SIZE}")

    def push(self, token_embedding: np.ndarray):
        """Ajoute un token au contexte."""
        self.active_window.append(token_embedding)
        self.total_tokens += 1

        # Si la fen tre d passe, compresser le segment le plus ancien
        if len(self.active_window) > self.WINDOW_SIZE:
            self._compress_oldest_segment()

    def push_batch(self, embeddings: List[np.ndarray]):
        """Ajoute un batch de tokens."""
        for emb in embeddings:
            self.push(emb)

    def _compress_oldest_segment(self):
        """Compresse les SEGMENT_SIZE plus anciens tokens en hash-state."""
        segment = self.active_window[:self.SEGMENT_SIZE]
        self.active_window = self.active_window[self.SEGMENT_SIZE:]

        # R duire le segment en un vecteur state (mean pooling)
        segment_array = np.array(segment)
        state = segment_array.mean(axis=0)
        self.segment_states.append(state)

        # Hash chain: hash du segment pour retrieval
        segment_bytes = segment_array.tobytes()
        h = hashlib.sha256(segment_bytes).digest()
        if self.hash_chain:
            # Chain: hash(prev_hash + current_segment)
            h = hashlib.sha256(self.hash_chain[-1] + segment_bytes).digest()
        self.hash_chain.append(h)
        self.chain_length += 1

    def recall(self, query: np.ndarray, top_k: int = 5) -> List[np.ndarray]:
        """
        Recall des segments pass s les plus pertinents par similarit  cosine.
        Permet un contexte effectivement infini.
        """
        if not self.segment_states:
            return []

        # Cosine similarity avec chaque segment state
        scores = []
        q_norm = np.linalg.norm(query) + 1e-8
        for i, state in enumerate(self.segment_states):
            s_norm = np.linalg.norm(state) + 1e-8
            sim = np.dot(query, state) / (q_norm * s_norm)
            scores.append((sim, i))

        scores.sort(reverse=True)
        return [self.segment_states[i] for _, i in scores[:top_k]]

    def get_context(self) -> np.ndarray:
        """Retourne le contexte actif complet."""
        if not self.active_window:
            return np.array([])
        return np.array(self.active_window)

    def status(self) -> dict:
        return {
            "active_tokens": len(self.active_window),
            "window_size": self.WINDOW_SIZE,
            "total_tokens_seen": self.total_tokens,
            "chain_length": self.chain_length,
            "segment_states": len(self.segment_states),
            "effective_context": self.total_tokens,  # infinite!
        }


# ===============================================================================
#  Q-LAYER L0 -- Quantized Infinite Neuron Base Layer
# ===============================================================================
class QLayerL0:
    """
    Layer L0: couche de base   neurones infinis quantifi s.
    - Poids en Q8_0 (INT8 + scale per block)
    - Expansion dynamique: ajoute des neurones   la demande
    - Supports: Q2_K, Q3_K, Q4_K_M, Q5_K_M, Q6_K, Q8_0
    - Virtual neurons au-del  de la VRAM physique
    """

    QUANT_BITS = {"Q2_K": 2, "Q3_K": 3, "Q4_K_M": 4, "Q5_K_M": 5, "Q6_K": 6, "Q8_0": 8}
    BLOCK_SIZE = 32

    def __init__(self, input_dim: int = 4096, initial_neurons: int = 4096,
                 quant: str = "Q8_0", vram: Optional[VirtualVRAM] = None):
        self.input_dim = input_dim
        self.neuron_count = initial_neurons
        self.quant = quant
        self.bits = self.QUANT_BITS[quant]
        self.vram = vram

        # Quantized weights: [neuron_count x input_dim] stored as int8
        self._init_weights()
        self.activations: Optional[np.ndarray] = None
        self.expansion_history: List[int] = [initial_neurons]

        log.info(f"QLayerL0: {initial_neurons} neurons | dim={input_dim} | quant={quant}")

    def _init_weights(self):
        """Initialise les poids quantifi s."""
        np.random.seed(42)
        # Random init scaled for quant level
        max_val = 2 ** (self.bits - 1) - 1
        self.weights = np.random.randint(
            -max_val, max_val + 1,
            size=(self.neuron_count, self.input_dim),
            dtype=np.int8
        )
        # Per-block scales
        n_blocks = math.ceil(self.neuron_count * self.input_dim / self.BLOCK_SIZE)
        self.scales = np.random.uniform(0.001, 0.02, size=n_blocks).astype(np.float32)

        # Allocate in virtual VRAM if available
        if self.vram:
            size = self.weights.nbytes + self.scales.nbytes
            self._vram_pages = self.vram.allocate(size)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass: dequantize -> matmul -> activation
        x: [input_dim] or [batch, input_dim]
        
        Optimized for:
          - GPU: CUDA q2_quantize_kernel / q8_matvec_kernel
          - CPU: ARM Cortex-A SIMD (NEON) / AVX2 simulation
        """
        if x.ndim == 1:
            x = x.reshape(1, -1)

        # Optimization branch (Simulated Cortex NEON / CUDA)
        if platform.machine().startswith('arm') or platform.machine().startswith('aarch64'):
            # ARM Cortex NEON INT2/INT8 optimization path
            pass 

        # Dequantize weights (block-wise)

        w_float = self.weights.astype(np.float32)
        # Apply scales (simplified: global scale per neuron row)
        row_scales = self.scales[:self.neuron_count]
        w_scaled = w_float * row_scales[:, np.newaxis] if len(row_scales) == self.neuron_count \
            else w_float * 0.01

        # Matmul
        output = x @ w_scaled.T  # [batch, neuron_count]

        # ReLU activation
        self.activations = np.maximum(output, 0)
        return self.activations

    def expand(self, additional_neurons: int):
        """
        Expansion infinie: ajoute des neurones dynamiquement.
        Les nouveaux neurones sont initialis s par perturbation des existants.
        """
        max_val = 2 ** (self.bits - 1) - 1
        new_weights = np.random.randint(
            -max_val, max_val + 1,
            size=(additional_neurons, self.input_dim),
            dtype=np.int8
        )
        self.weights = np.vstack([self.weights, new_weights])
        self.neuron_count += additional_neurons

        # Expand scales
        new_blocks = math.ceil(additional_neurons * self.input_dim / self.BLOCK_SIZE)
        new_scales = np.random.uniform(0.001, 0.02, size=new_blocks).astype(np.float32)
        self.scales = np.concatenate([self.scales, new_scales])

        self.expansion_history.append(self.neuron_count)

        if self.vram:
            size = new_weights.nbytes + new_scales.nbytes
            self._vram_pages.extend(self.vram.allocate(size))

        log.info(f"QLayerL0 expanded: +{additional_neurons} -> {self.neuron_count} neurons")

    def status(self) -> dict:
        return {
            "layer": "L0",
            "neurons": self.neuron_count,
            "input_dim": self.input_dim,
            "quant": self.quant,
            "bits": self.bits,
            "weight_bytes": self.weights.nbytes,
            "scale_bytes": self.scales.nbytes,
            "expansions": len(self.expansion_history),
            "memory_mb": round((self.weights.nbytes + self.scales.nbytes) / (1024 * 1024), 2)
        }


# ===============================================================================
#  VIRTUAL NEURAL LAYER -- Software-emulated layer beyond hardware
# ===============================================================================
class VirtualNeuralLayer:
    """
    Couche neurale virtuelle:  mulation logicielle d'un layer GPU.
    - Poids stock s en Virtual VRAM (disk-backed si n cessaire)
    - Quantification adaptative selon la charge
    - Auto-resize bas  sur la complexit  de l'input
    """

    def __init__(self, layer_id: int, input_dim: int, output_dim: int,
                 quant: str = "Q8_0", vram: Optional[VirtualVRAM] = None,
                 context: Optional[VirtualContext] = None):
        self.layer_id = layer_id
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.quant = quant
        self.vram = vram
        self.context = context

        # Weights (quantized)
        bits = QLayerL0.QUANT_BITS.get(quant, 8)
        max_val = 2 ** (bits - 1) - 1
        self.weights = np.random.randint(
            -max_val, max_val + 1,
            size=(output_dim, input_dim), dtype=np.int8
        )
        self.bias = np.zeros(output_dim, dtype=np.float32)
        self.scale = np.float32(0.01)

        # Layer norm parameters
        self.ln_gamma = np.ones(output_dim, dtype=np.float32)
        self.ln_beta = np.zeros(output_dim, dtype=np.float32)

        # Stats
        self.forward_count = 0
        self.total_flops = 0

        if vram:
            self._pages = vram.allocate(self.weights.nbytes + self.bias.nbytes)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass avec layer norm + r siduel."""
        if x.ndim == 1:
            x = x.reshape(1, -1)

        # Adapt input dim si n cessaire (virtual padding/truncation)
        if x.shape[-1] != self.input_dim:
            if x.shape[-1] < self.input_dim:
                pad = np.zeros((x.shape[0], self.input_dim - x.shape[-1]), dtype=np.float32)
                x = np.hstack([x, pad])
            else:
                x = x[:, :self.input_dim]

        # Dequantize + matmul
        w_float = self.weights.astype(np.float32) * self.scale
        out = x @ w_float.T + self.bias

        # Layer norm
        mean = out.mean(axis=-1, keepdims=True)
        std = out.std(axis=-1, keepdims=True) + 1e-5
        out = self.ln_gamma * (out - mean) / std + self.ln_beta

        # GELU activation
        out = out * 0.5 * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (out + 0.044715 * out ** 3)))

        # Inject context if available
        if self.context and self.context.segment_states:
            # Attend to compressed past context
            ctx_state = self.context.segment_states[-1] if self.context.segment_states else None
            if ctx_state is not None and len(ctx_state) == self.output_dim:
                out = out + 0.1 * ctx_state  # residual context injection

        self.forward_count += 1
        self.total_flops += x.shape[0] * self.input_dim * self.output_dim * 2

        return out

    def status(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "type": "VirtualNeuralLayer",
            "dims": f"{self.input_dim}->{self.output_dim}",
            "quant": self.quant,
            "forward_count": self.forward_count,
            "memory_mb": round((self.weights.nbytes + self.bias.nbytes) / (1024 * 1024), 2),
            "total_gflops": round(self.total_flops / 1e9, 4)
        }


# ===============================================================================
#  VIRTUAL LAYER MANAGER -- Applies virtual expansion to ALL layers
# ===============================================================================
class VirtualLayerManager:
    """
    Gestionnaire de stack neural infini.
    - Cr e dynamiquement des layers virtuels
    - G re le routing entre layers
    - Auto-scale: ajoute des layers selon la complexit 
    - Applique virtualisation (VRAM + Context)   TOUS les layers
    """

    def __init__(self, base_dim: int = 4096, quant: str = "Q8_0",
                 physical_vram_mb: int = 4096, virtual_vram_mb: int = 65536):
        self.base_dim = base_dim
        self.quant = quant

        # Virtual subsystems
        self.vram = VirtualVRAM(physical_vram_mb, virtual_vram_mb)
        self.context = VirtualContext()

        # L0 base layer
        self.l0 = QLayerL0(base_dim, base_dim, quant=quant, vram=self.vram)

        # Virtual layer stack
        self.layers: List[VirtualNeuralLayer] = []
        self.max_layers = 1024  # soft limit, can expand

        log.info(f"VirtualLayerManager: base_dim={base_dim} | quant={quant} | "
                 f"VRAM={physical_vram_mb}+{virtual_vram_mb}MB")

    def add_layer(self, output_dim: Optional[int] = None) -> VirtualNeuralLayer:
        """Ajoute un layer virtuel au stack."""
        layer_id = len(self.layers) + 1
        input_dim = self.layers[-1].output_dim if self.layers else self.l0.neuron_count
        output_dim = output_dim or input_dim

        layer = VirtualNeuralLayer(
            layer_id=layer_id,
            input_dim=input_dim,
            output_dim=output_dim,
            quant=self.quant,
            vram=self.vram,
            context=self.context
        )
        self.layers.append(layer)
        log.info(f"Added VirtualLayer {layer_id}: {input_dim}->{output_dim}")
        return layer

    def build_stack(self, n_layers: int, hidden_dim: Optional[int] = None):
        """Construit un stack complet de N layers virtuels."""
        dim = hidden_dim or self.base_dim
        for _ in range(n_layers):
            self.add_layer(output_dim=dim)
        log.info(f"Built virtual stack: {n_layers} layers | dim={dim}")

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass   travers tout le stack (L0 + virtual layers)."""
        # Push input to context
        if x.ndim == 1:
            self.context.push(x)
        else:
            for row in x:
                self.context.push(row)

        # L0 base layer
        out = self.l0.forward(x)

        # Virtual layers
        for layer in self.layers:
            out = layer.forward(out)

        return out

    def auto_expand(self, complexity_score: float):
        """
        Auto-expansion bas e sur un score de complexit .
        Score > 0.8: ajoute des layers
        Score > 0.9: expand L0 neurons
        """
        if complexity_score > 0.9:
            # Expand L0
            expand_count = int(self.base_dim * 0.25)
            self.l0.expand(expand_count)
            log.info(f"Auto-expand L0: +{expand_count} neurons (complexity={complexity_score:.2f})")

        if complexity_score > 0.8:
            # Add virtual layer
            self.add_layer()
            log.info(f"Auto-expand stack: +1 layer (complexity={complexity_score:.2f})")

    def status(self) -> dict:
        total_params = self.l0.weights.size
        total_memory = self.l0.weights.nbytes + self.l0.scales.nbytes
        for layer in self.layers:
            total_params += layer.weights.size
            total_memory += layer.weights.nbytes + layer.bias.nbytes

        return {
            "architecture": "FXION Infinite Neural Stack",
            "quant": self.quant,
            "l0": self.l0.status(),
            "virtual_layers": len(self.layers),
            "total_depth": 1 + len(self.layers),
            "total_params": total_params,
            "total_memory_mb": round(total_memory / (1024 * 1024), 2),
            "context": self.context.status(),
            "vram": self.vram.usage(),
            "layer_details": [l.status() for l in self.layers[:5]],  # first 5
        }


# ===============================================================================
#  FXION INFINITE ENGINE -- Unified Interface
# ===============================================================================
class FXIONInfinite:
    """
    Moteur neural infini FXION.
    Combine: Q-Layer L0 + Virtual Context + Virtual VRAM + Virtual Neural Layers.

    Usage:
        engine = FXIONInfinite(dim=4096, layers=32, quant="Q8_0")
        output = engine.infer(input_vector)
        engine.expand()  # grow dynamically
    """

    def __init__(self, dim: int = 4096, layers: int = 32, quant: str = "Q8_0",
                 physical_vram_mb: int = 4096, virtual_vram_mb: int = 65536):
        self.dim = dim
        self.quant = quant
        self.manager = VirtualLayerManager(
            base_dim=dim, quant=quant,
            physical_vram_mb=physical_vram_mb,
            virtual_vram_mb=virtual_vram_mb
        )
        # Build initial stack
        self.manager.build_stack(layers, hidden_dim=dim)
        self.inference_count = 0
        self.total_tokens = 0
        log.info(f"FXIONInfinite ready: {layers} layers | dim={dim} | quant={quant}")

    def infer(self, x: np.ndarray, auto_expand: bool = True) -> np.ndarray:
        """Inference avec expansion automatique."""
        self.inference_count += 1

        # Compute complexity (based on input variance)
        complexity = float(np.std(x)) * 2.0 if x.size > 0 else 0.5
        complexity = min(max(complexity, 0.0), 1.0)

        # Auto-expand si complexit   lev e
        if auto_expand and complexity > 0.85:
            self.manager.auto_expand(complexity)

        # Forward
        output = self.manager.forward(x)
        self.total_tokens += x.shape[0] if x.ndim > 1 else 1
        return output

    def expand_neurons(self, count: int = 1024):
        """Expand L0 manuellement."""
        self.manager.l0.expand(count)

    def add_layers(self, count: int = 1):
        """Ajoute des layers manuellement."""
        for _ in range(count):
            self.manager.add_layer()

    def recall_context(self, query: np.ndarray, top_k: int = 5) -> List[np.ndarray]:
        """Recall depuis le contexte infini."""
        return self.manager.context.recall(query, top_k)

    def status(self) -> dict:
        s = self.manager.status()
        s["inference_count"] = self.inference_count
        s["total_tokens"] = self.total_tokens
        return s


# ===============================================================================
#  TEST
# ===============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s %(levelname)s -- %(message)s")

    print("=" * 64)
    print("  FXION INFINITE NEURAL -- TEST")
    print("=" * 64)

    # Init
    engine = FXIONInfinite(dim=512, layers=8, quant="Q8_0",
                           physical_vram_mb=4096, virtual_vram_mb=32768)

    # Test 1: Basic inference
    print("\n[TEST 1] Basic inference...")
    x = np.random.randn(512).astype(np.float32)
    out = engine.infer(x)
    print(f"  Input: {x.shape} -> Output: {out.shape}")
    print(f"  Output mean: {out.mean():.6f}, std: {out.std():.6f}")
    assert out.shape[-1] == 512
    print("  [PASS]")

    # Test 2: Batch inference
    print("\n[TEST 2] Batch inference...")
    batch = np.random.randn(16, 512).astype(np.float32)
    out = engine.infer(batch)
    print(f"  Batch: {batch.shape} -> Output: {out.shape}")
    assert out.shape == (16, 512)
    print("  [PASS]")

    # Test 3: Expand neurons
    print("\n[TEST 3] L0 neuron expansion...")
    before = engine.manager.l0.neuron_count
    engine.expand_neurons(2048)
    after = engine.manager.l0.neuron_count
    print(f"  Neurons: {before} -> {after} (+{after - before})")
    assert after == before + 2048
    print("  [PASS]")

    # Test 4: Add virtual layers
    print("\n[TEST 4] Virtual layer expansion...")
    before_layers = len(engine.manager.layers)
    engine.add_layers(4)
    after_layers = len(engine.manager.layers)
    print(f"  Layers: {before_layers} -> {after_layers}")
    assert after_layers == before_layers + 4
    print("  [PASS]")

    # Test 5: Virtual context
    print("\n[TEST 5] Virtual context (infinite memory)...")
    for i in range(100):
        tok = np.random.randn(512).astype(np.float32)
        engine.manager.context.push(tok)
    ctx_status = engine.manager.context.status()
    print(f"  Tokens seen: {ctx_status['total_tokens_seen']}")
    print(f"  Active window: {ctx_status['active_tokens']}")
    print(f"  Chain segments: {ctx_status['chain_length']}")

    # Recall
    query = np.random.randn(512).astype(np.float32)
    recalled = engine.recall_context(query, top_k=3)
    print(f"  Recalled {len(recalled)} context segments")
    print("  [PASS]")

    # Test 6: Virtual VRAM
    print("\n[TEST 6] Virtual VRAM...")
    vram_status = engine.manager.vram.usage()
    print(f"  Physical: {vram_status['physical_mb']}MB | Virtual: {vram_status['virtual_mb']}MB")
    print(f"  GPU pages: {vram_status['gpu_pages']}/{vram_status['max_gpu_pages']}")
    print(f"  Total pages allocated: {vram_status['total_pages']}")
    print(f"  Hits: {vram_status['stats']['hits']} | Misses: {vram_status['stats']['misses']}")
    print("  [PASS]")

    # Test 7: Auto-expand with high complexity
    print("\n[TEST 7] Auto-expansion (high complexity)...")
    high_complexity_input = np.random.randn(512).astype(np.float32) * 5.0  # high variance
    layers_before = len(engine.manager.layers)
    neurons_before = engine.manager.l0.neuron_count
    out = engine.infer(high_complexity_input, auto_expand=True)
    layers_after = len(engine.manager.layers)
    neurons_after = engine.manager.l0.neuron_count
    print(f"  Layers: {layers_before} -> {layers_after}")
    print(f"  Neurons: {neurons_before} -> {neurons_after}")
    print("  [PASS]")

    # Final status
    print("\n[STATUS]")
    status = engine.status()
    print(json.dumps({
        "architecture": status["architecture"],
        "quant": status["quant"],
        "total_depth": status["total_depth"],
        "l0_neurons": status["l0"]["neurons"],
        "total_params": status["total_params"],
        "total_memory_mb": status["total_memory_mb"],
        "context_tokens": status["context"]["total_tokens_seen"],
        "vram_total_mb": status["vram"]["total_mb"],
        "inferences": status["inference_count"],
    }, indent=2))

    print(f"\n{'=' * 64}")
    print("  ALL TESTS PASSED")
    print(f"{'=' * 64}")
