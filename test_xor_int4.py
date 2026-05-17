
"""
FXION XOR-INT4 VERIFIER
Verifies the implementation of XOR-obfuscated INT4 quantization.
"""
import numpy as np
import qfx_quant as q

def test_xor_q4():
    print("=== FXION XOR-INT4 QUANTIZATION TEST ===")
    
    # Data
    N = 1024
    weights = np.random.randn(N).astype(np.float32)
    mask = 0x0A  # Example XOR mask (1010)
    
    # XOR Quantize
    xq4, scales = q.quantize_xor_q4(weights, xor_mask=mask)
    
    # Dequantize
    recon = q.dequantize_xor_q4(xq4, scales, xor_mask=mask)
    
    error = q.mae(weights, recon)
    
    print(f"Mask used: {bin(mask)}")
    print(f"XOR-INT4 MAE: {error:.6f}")
    
    if error < 0.5:
        print("[SUCCESS] XOR-INT4 pipeline is functional.")
    else:
        print("[FAIL] High error detected.")

if __name__ == "__main__":
    test_xor_q4()
