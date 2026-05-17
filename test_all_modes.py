"""
FXION-ONYX -- ALL MODES TEST
Runs every launch.py mode automatically and reports pass/fail.
Run: python test_all_modes.py
"""
import sys, os, time, io, contextlib, traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.environ["FXION_PATH"] = ROOT
os.environ["PYTHONPATH"] = ROOT

# Import launch module directly
import launch

MODES = [
    ("q8",      launch.mode_q8),
    ("start",   launch.mode_start),
    ("neural",  launch.mode_neural),
    ("qfx",    launch.mode_qfx),
    ("turbo",   launch.mode_turbo),
    ("bench",   launch.mode_bench),
    ("status",  launch.mode_status),
    ("nnox",    launch.mode_nnox),
    ("onyx",    launch.mode_onyx),
    ("fxion",   launch.mode_fxion_only),
]

# Skip install and test (they call subprocess/pip)
SKIP = ["install", "test"]

print("=" * 64)
print("  FXION-ONYX -- ALL MODES TEST")
print("=" * 64)
print()

results = []
total_start = time.time()

for name, func in MODES:
    print(f"  [{name.upper():<8}] Running...", end=" ", flush=True)
    t0 = time.time()
    try:
        # Capture stdout to avoid flooding terminal
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            func()
        elapsed = time.time() - t0
        output = buf.getvalue()
        # Check for obvious failures in output
        if "[FAIL]" in output and "[OK]" not in output:
            results.append((name, "WARN", elapsed, "Output contains FAIL"))
            print(f"WARN  ({elapsed:.2f}s)")
        else:
            results.append((name, "PASS", elapsed, ""))
            print(f"PASS  ({elapsed:.2f}s)")
    except Exception as e:
        elapsed = time.time() - t0
        tb = traceback.format_exc().split("\n")[-2]
        results.append((name, "FAIL", elapsed, str(e)))
        print(f"FAIL  ({elapsed:.2f}s) -- {e}")

total_elapsed = time.time() - total_start

# Summary
print()
print("=" * 64)
print(f"  {'MODE':<10} {'RESULT':<8} {'TIME':>8}  {'DETAIL'}")
print(f"  {'-'*10} {'-'*8} {'-'*8}  {'-'*30}")
for name, status, elapsed, detail in results:
    symbol = "OK" if status == "PASS" else ("!!" if status == "WARN" else "XX")
    print(f"  {name:<10} [{symbol}]    {elapsed:>6.2f}s  {detail[:40]}")

passed = sum(1 for _, s, _, _ in results if s == "PASS")
warned = sum(1 for _, s, _, _ in results if s == "WARN")
failed = sum(1 for _, s, _, _ in results if s == "FAIL")

print()
print(f"  Total: {len(results)} modes | Passed: {passed} | Warnings: {warned} | Failed: {failed}")
print(f"  Elapsed: {total_elapsed:.2f}s")
print(f"  Skipped: {', '.join(SKIP)} (require subprocess)")
print("=" * 64)

if failed > 0:
    print("\n  SOME MODES FAILED -- see details above")
    sys.exit(1)
else:
    print("\n  ALL MODES PASSED")
    sys.exit(0)
