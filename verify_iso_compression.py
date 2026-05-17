
"""
FXION ISO COMPRESSION VERIFIER
Calculates and verifies the best compression ratios for ISO deployment.
Targeting Q2_K (INT2) for maximum efficiency on ARM Cortex / GTX 970.
"""
import os, math
import numpy as np
import qfx_quant as q

def verify_compression():
    print("=== FXION ISO COMPRESSION ANALYSIS ===")
    
    # Simulate a typical LLM weight block (4096 params)
    N = 4096
    weights = np.random.randn(N).astype(np.float32)
    original_size = weights.nbytes
    
    # Test Q8
    q8, s8 = q.quantize_q8(weights)
    q8_size = q8.nbytes + s8.nbytes
    q8_mae = q.mae(weights, q.dequantize_q8(q8, s8))
    
    # Test Q4
    q4, s4 = q.quantize_q4(weights)
    q4_size = (q4.nbytes // 2) + s4.nbytes  # Simulated 4-bit packing
    q4_mae = q.mae(weights, q.dequantize_q8(q4, s4))
    
    # Test Q2 (Best Compression)
    q2, s2 = q.quantize_q2(weights)
    q2_size = (q2.nbytes // 4) + s2.nbytes  # Simulated 2-bit packing
    q2_mae = q.mae(weights, q.dequantize_q8(q2, s2))
    
    print(f"Original Size: {original_size / 1024:.2f} KB")
    print("-" * 40)
    print(f"Mode: Q8_0 (8-bit)")
    print(f"  Size: {q8_size / 1024:.2f} KB ({original_size/q8_size:.1f}x)")
    print(f"  MAE:  {q8_mae:.6f}")
    
    print(f"Mode: Q4_K (4-bit)")
    print(f"  Size: {q4_size / 1024:.2f} KB ({original_size/q4_size:.1f}x)")
    print(f"  MAE:  {q4_mae:.6f}")
    
    print(f"Mode: Q2_K (2-bit) [*] BEST COMPRESSION [*]")
    print(f"  Size: {q2_size / 1024:.2f} KB ({original_size/q2_size:.1f}x)")
    print(f"  MAE:  {q2_mae:.6f}")
    print("-" * 40)
    
    # Best Layer Configuration
    best_config = {
        "kernel": "q2_quantize_kernel",
        "compression_ratio": original_size / q2_size,
        "recommended_layers": ["QLayerL0", "VirtualNeuralLayer"],
        "iso_optimization": "CORTEX_INT2_NEON"
    }
    
    print(f"ISO Deployment Suggestion: Use {best_config['iso_optimization']} for layers.")
    return best_config

if __name__ == "__main__":
    verify_compression()
