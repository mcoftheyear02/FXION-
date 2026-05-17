"""
DEEP-LEARN SDK — Dynamic Mathematic Entropic Graph
Builds a small directed neural graph, runs forward pass with entropy tracking,
and reports node-level entropy + spectral graph metrics.
"""
import math
import random
import numpy as np


def build_graph(nodes: int = 16, density: float = 0.35, seed: int = 21) -> dict:
    rng = np.random.default_rng(seed)
    W = (rng.standard_normal((nodes, nodes)) * (rng.random((nodes, nodes)) < density).astype(float)).astype(np.float32)
    W = W * 0.4
    return {"W": W, "nodes": nodes}


def gelu(x):
    return 0.5 * x * (1.0 + np.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x ** 3)))


def shannon(p):
    p = np.asarray(p, dtype=np.float32)
    p = p[p > 0]
    if len(p) == 0:
        return 0.0
    p = p / p.sum()
    return float(-(p * np.log2(p)).sum())


def forward(graph: dict, steps: int = 8, seed: int = 7) -> dict:
    W = graph["W"]
    n = graph["nodes"]
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32) * 0.5
    trace = []
    for t in range(steps):
        z = gelu(W @ x)
        # softmax for entropy probability
        e = np.exp(z - z.max())
        p = e / e.sum()
        h = shannon(p)
        trace.append({
            "step": t,
            "entropy_bits": round(h, 4),
            "max_activation": round(float(z.max()), 4),
            "mean_activation": round(float(z.mean()), 4),
            "l2_norm": round(float(np.linalg.norm(z)), 4),
        })
        x = z / max(1.0, np.linalg.norm(z))
    # spectral radius
    try:
        eig = np.linalg.eigvals(W)
        radius = float(np.max(np.abs(eig)))
    except Exception:
        radius = 0.0
    return {
        "graph_nodes": n,
        "edges_nonzero": int(np.count_nonzero(W)),
        "spectral_radius": round(radius, 4),
        "final_entropy_bits": trace[-1]["entropy_bits"],
        "avg_entropy_bits": round(sum(t["entropy_bits"] for t in trace) / len(trace), 4),
        "steps": trace,
    }


def run(nodes: int = 16, steps: int = 8, density: float = 0.35) -> dict:
    g = build_graph(nodes=max(4, min(nodes, 64)), density=density)
    return forward(g, steps=max(2, min(steps, 24)))
