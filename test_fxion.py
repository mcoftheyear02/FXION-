"""
FXION MODULE TEST SUITE
Run: python test_fxion.py
"""
import sys, json
sys.path.insert(0, ".")

print("=" * 60)
print("  FXION MODULE TEST SUITE")
print("=" * 60)

errors = 0

# --- TEST 1: Imports -----------------------------------------
print("\n[TEST 1] Imports...")
try:
    from fxion import FXIONEngine, FXIONQuantizer, PCIeBridge
    print("  PASS -- all classes imported")
except Exception as e:
    print(f"  FAIL -- {e}")
    errors += 1

# --- TEST 2: FXIONEngine -------------------------------------
print("\n[TEST 2] FXIONEngine...")
try:
    engine = FXIONEngine(vram_budget_gb=4.0)
    assert engine.vram_budget == 4.0
    assert engine.model_loaded == False
    assert engine.active_quant is None

    # Load model
    ok = engine.load_model("Q8_0")
    assert ok == True
    assert engine.active_quant == "Q8_0"
    assert engine.model_loaded == True

    # Reject invalid quant
    ok = engine.load_model("INVALID")
    assert ok == False

    # Reject over-budget
    engine2 = FXIONEngine(vram_budget_gb=1.0)
    ok = engine2.load_model("Q8_0")  # needs 3.8GB
    assert ok == False

    # Inference
    result = engine.infer("Hello world", max_tokens=64)
    assert result.quant == "Q8_0"
    assert result.tokens == 64
    assert result.tps > 0
    assert result.latency_ms > 0
    assert result.accuracy == 0.991

    # Multiple inferences
    for _ in range(5):
        engine.infer("test", max_tokens=32)
    assert engine.session_id == 6

    # Status
    s = engine.status()
    assert s["engine"] == "FXION"
    assert s["active_quant"] == "Q8_0"
    assert s["sessions"] == 6

    print(f"  PASS -- engine works | tps={result.tps} | sessions={engine.session_id}")
except Exception as e:
    print(f"  FAIL -- {e}")
    errors += 1

# --- TEST 3: FXIONQuantizer ----------------------------------
print("\n[TEST 3] FXIONQuantizer...")
try:
    import numpy as np
    np.random.seed(42)
    weights = np.random.randn(4096).astype(np.float32) * 0.02

    fq = FXIONQuantizer(block_size=32)

    # Q8
    q8, scales8 = fq.quantize_q8(weights)
    assert q8.dtype == np.int8
    assert len(q8) == 4096
    assert len(scales8) == 128  # 4096/32

    recon8 = fq.dequantize_q8(q8, scales8)
    mae8 = float(np.mean(np.abs(weights - recon8)))
    assert mae8 < 0.001, f"Q8 MAE too high: {mae8}"

    # Q4
    q4, scales4 = fq.quantize_q4(weights)
    assert q4.dtype == np.int8
    assert all(q4 >= -7) and all(q4 <= 7)

    # Pipeline
    report = fq.pipeline(weights, "Q8_0")
    assert report["mode"] == "Q8_0"
    assert report["compression"] > 1.0
    assert report["error"]["mae"] < 0.001

    # Stats
    assert fq.stats["q8_calls"] == 2
    assert fq.stats["q4_calls"] == 1

    print(f"  PASS -- Q8 MAE={mae8:.6f} | compression={report['compression']}x")
except ImportError:
    print("  SKIP -- numpy not installed")
except Exception as e:
    print(f"  FAIL -- {e}")
    errors += 1

# --- TEST 4: PCIeBridge --------------------------------------
print("\n[TEST 4] PCIeBridge...")
try:
    bridge = PCIeBridge()
    assert bridge.vram_limit_mb == 4096.0
    assert bridge.vram_allocated_mb == 0.0

    # Alloc
    ok = bridge.alloc(3820)
    assert ok == True
    assert bridge.vram_allocated_mb == 3820.0

    # Over-alloc should fail
    ok = bridge.alloc(500)
    assert ok == False

    # Free
    bridge.free(1000)
    assert bridge.vram_allocated_mb == 2820.0

    bridge.free_all()
    assert bridge.vram_allocated_mb == 0.0

    # Transfer
    t = bridge.transfer_h2d(1024 * 1024 * 100)  # 100MB
    assert t.direction == "H2D"
    assert t.bytes_transferred == 104857600
    assert t.elapsed_ms > 0
    assert t.bandwidth_gbps > 0

    t2 = bridge.transfer_d2h(1024 * 1024 * 50)
    assert t2.direction == "D2H"
    assert len(bridge.transfers) == 2

    # Status
    s = bridge.status()
    assert s["pcie"] == "Gen3 x16"
    assert s["transfers"] == 2

    print(f"  PASS -- H2D: {t.elapsed_ms}ms @ {t.bandwidth_gbps} GB/s | VRAM alloc/free OK")
except Exception as e:
    print(f"  FAIL -- {e}")
    errors += 1

# --- TEST 5: Benchmark ---------------------------------------
print("\n[TEST 5] Engine benchmark...")
try:
    engine = FXIONEngine(vram_budget_gb=4.0)
    results = engine.benchmark(iterations=3)
    assert len(results) == 6
    assert "Q8_0" in results
    assert results["Q8_0"]["accuracy"] == 0.991
    assert results["Q8_0"]["avg_tps"] > 100

    # Print table
    print(f"  {'Quant':<10} {'TPS':>6} {'VRAM':>6} {'Acc':>6} {'Score':>7}")
    for q, r in results.items():
        marker = " [*]" if q == "Q8_0" else ""
        print(f"  {q:<10} {r['avg_tps']:>6.1f} {r['vram_gb']:>5.1f}G {r['accuracy']:>5.1%} {r['score']:>7.4f}{marker}")

    print(f"  PASS -- all 6 quant levels benchmarked")
except Exception as e:
    print(f"  FAIL -- {e}")
    errors += 1

# --- SUMMARY -------------------------------------------------
print("\n" + "=" * 60)
if errors == 0:
    print("  ALL TESTS PASSED [OK]")
else:
    print(f"  {errors} TEST(S) FAILED [ERR]")
print("=" * 60)
sys.exit(errors)
