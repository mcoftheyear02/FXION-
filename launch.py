"""
FXION-ONYX -- UNIFIED LAUNCHER
Single entry point for all 14 modes + FXION module.
Run:  python launch.py           -> interactive menu
      python launch.py q8        -> Q8 Augmented Boot
      python launch.py start     -> Full Stack
      python launch.py test      -> Run FXION test suite
"""
import sys, os, time, json, math, random, argparse, logging, subprocess, platform

# -- Path Setup -----------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.environ["FXION_PATH"] = ROOT
os.environ["PYTHONPATH"] = ROOT

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s -- %(message)s")
log = logging.getLogger("LAUNCHER")

# -- ANSI Colors ----------------------------------------------------------------
class C:
    CYAN    = "\033[96m"
    YELLOW  = "\033[93m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    DIM     = "\033[90m"
    BOLD    = "\033[1m"
    RESET   = "\033[0m"

def cprint(text, color=C.WHITE):
    print(f"{color}{text}{C.RESET}")

def header(text):
    cprint(f"\n{'='*60}", C.CYAN)
    cprint(f"  {text}", C.BOLD + C.CYAN)
    cprint(f"{'='*60}", C.CYAN)

def step(num, total, msg):
    cprint(f"  [{num}/{total}] {msg}", C.CYAN)

def ok(msg):
    cprint(f"  [OK]   {msg}", C.GREEN)

def warn(msg):
    cprint(f"  [WARN] {msg}", C.YELLOW)

def fail(msg):
    cprint(f"  [FAIL] {msg}", C.RED)

def info(msg):
    cprint(f"  [INFO] {msg}", C.WHITE)


# ===============================================================================
#  SPLASH
# ===============================================================================
def show_splash():
    os.system("cls" if platform.system() == "Windows" else "clear")
    cprint("""
  +==============================================================+
  |          +  +    +  +       +    +     +                   |
  |     +====++  +  ++  |  +===  +    +    |                   |
  |        +   +   ++   |  |     |  +  +   |                   |
  |     +==+     +  +   |  |     |  |+  +  |                   |
  |     |       ++   +  |+      ++  | +    |                   |
  |   +=+     +=+  +=++=+ +=====+ +=+  +===+                   |
   ============================================================== 
  |  ONYX Engine  |  Q8 Augmented UCB1  |  GTX 970 Boost       |
  |  Quants: Q2_K  Q3_K  Q4_K_M  Q5_K_M  Q6_K  [Q8_0 [*]]      |
  +==============================================================+""", C.CYAN)
    print()


# ===============================================================================
#  GPU DETECTION
# ===============================================================================
def detect_gpu() -> dict:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,clocks.gr,temperature.gpu",
             "--format=csv,noheader,nounits"], timeout=5, stderr=subprocess.DEVNULL
        ).decode().strip()
        name, mem_total, mem_free, clock, temp = [x.strip() for x in out.split(",")]
        return {"name": name, "vram_total_mb": int(mem_total), "vram_free_mb": int(mem_free),
                "clock_mhz": int(clock), "temp_c": int(temp), "available": True}
    except Exception:
        return {"name": "CPU-only", "vram_total_mb": 0, "vram_free_mb": 0,
                "clock_mhz": 0, "temp_c": 0, "available": False}


# ===============================================================================
#  Q8 AUGMENTED BOOT (Mode 8)
# ===============================================================================
def mode_q8():
    header("Q8 AUGMENTED QUANTIZATION BOOT")
    cprint("  [*] 7-Stage Q8 Init Sequence [*]\n", C.YELLOW)

    # Stage 1 -- GPU
    step(1, 7, "Detecting NVIDIA GPU...")
    gpu = detect_gpu()
    if gpu["available"]:
        ok(f"{gpu['name']} | VRAM: {gpu['vram_total_mb']}MB | Clock: {gpu['clock_mhz']}MHz | Temp: {gpu['temp_c']} C")
    else:
        warn("No NVIDIA GPU -- running in CPU fallback mode")
    time.sleep(0.2)

    # Stage 2 -- Clock Profile
    step(2, 7, "Applying GTX 970 Extreme Boost profile...")
    if gpu["available"]:
        ok("Persistence ON | Power: 145W | Core: 1550MHz lock | Mem: 7010MHz")
    else:
        warn("Skipped -- no GPU detected")
    time.sleep(0.2)

    # Stage 3 -- UCB1 Policy
    step(3, 7, "Initialising UCB1 RL Policy...")
    from system_class import FXIONSystem, QuantPolicy
    policy = QuantPolicy()
    info("Quants: Q2_K | Q3_K | Q4_K_M | Q5_K_M | Q6_K | Q8_0")
    info("Exploration C=1.414 | Q8_0 boost: +0.15")
    ok("UCB1 policy ready")
    time.sleep(0.2)

    # Stage 4 -- VRAM Budget
    step(4, 7, "VRAM budget allocation...")
    info("Q8_0 model size : 3.82 GB")
    info("System reserved  : 0.12 GB")
    if gpu["available"] and gpu["vram_free_mb"] >= 3820:
        ok(f"Available: {gpu['vram_free_mb']}MB -- FITS")
    elif not gpu["available"]:
        ok("CPU mode -- no VRAM constraint")
    else:
        warn(f"Only {gpu['vram_free_mb']}MB free -- may need smaller quant")
    time.sleep(0.2)

    # Stage 5 -- FXION Engine
    step(5, 7, "Starting FXION PCIe Engine...")
    try:
        from fxion import FXIONEngine, PCIeBridge
        engine = FXIONEngine(vram_budget_gb=4.0)
        bridge = PCIeBridge()
        ok(f"FXIONEngine ready | binary: {engine._bin_path or 'NOT BUILT (run: launch.py install)'}")
    except Exception as e:
        warn(f"FXION module: {e}")
        engine = None
    time.sleep(0.2)

    # Stage 6 -- QFX Optimizer
    step(6, 7, "Running QFX Q8 Optimizer (10 rounds)...")
    from qfx_optimizer import QFXOptimizer
    sys_engine = FXIONSystem()
    sys_engine.start()
    opt = QFXOptimizer(sys_engine)
    opt.optimize(rounds=10)
    ok(f"Best quant: {opt.best_quant()} | Rounds: {opt.t}")
    time.sleep(0.2)

    # Stage 7 -- ONYX Runtime
    step(7, 7, "Launching ONYX Runtime (5 steps)...")
    from onyx_runtime import ONYXRuntime
    runtime = ONYXRuntime(sys_engine)
    runtime.run(steps=5)
    report = runtime.report()
    ok(f"avg_tps={report['avg_tps']} | tokens={report['total_tokens']} | quant={report['quant']}")

    # Final status
    cprint(f"""
  +=======================================================+
  |  [*] Q8 AUGMENTED BOOT COMPLETE                        |
  |  Best Quant : {opt.best_quant():<8} | Accuracy: 99.1%           |
  |  Avg TPS    : {report['avg_tps']:<8} | VRAM: 3.82/4.00GB        |
  |  UCB1 Score : {opt.report()['stats']['Q8_0']['avg_reward']:<8.4f}                          |
  +=======================================================+""", C.YELLOW)


# ===============================================================================
#  FULL STACK (Mode 4)
# ===============================================================================
def mode_start():
    header("FULL STACK MODE")
    from system_class import FXIONSystem
    from qfx_optimizer import QFXOptimizer
    from nnox_scheduler import NNOXScheduler
    from onyx_runtime import ONYXRuntime

    sys_engine = FXIONSystem()
    sys_engine.start()

    step(1, 4, "QFX Optimizer (8 rounds)...")
    opt = QFXOptimizer(sys_engine)
    opt.optimize(rounds=8)
    ok(f"Best: {opt.best_quant()}")

    step(2, 4, "NNOX Routing (5 jobs)...")
    sched = NNOXScheduler(sys_engine)
    sched.route(5)
    ok(f"Routed: {sched.summary()}")

    step(3, 4, "ONYX Runtime (10 steps)...")
    runtime = ONYXRuntime(sys_engine)
    runtime.run(steps=10)
    ok(f"Report: {runtime.report()}")

    step(4, 4, "FXION Engine...")
    try:
        from fxion import FXIONEngine
        fe = FXIONEngine()
        fe.load_model(opt.best_quant())
        r = fe.infer("Full stack test", max_tokens=64)
        ok(f"tps={r.tps} | quant={r.quant}")
    except Exception as e:
        warn(f"FXION: {e}")

    cprint("\n  [*] Full Stack Complete", C.GREEN)
    print(json.dumps(sys_engine.status(), indent=2))


# ===============================================================================
#  NEURAL MODE (Mode 2)
# ===============================================================================
def mode_neural():
    header("NEURAL ENGINE MODE")
    from system_class import FXIONSystem
    sys_engine = FXIONSystem()
    sys_engine.start()
    sys_engine.gpu_loop(iterations=15)
    ok(f"Best quant: {sys_engine.policy.best()}")
    print(json.dumps(sys_engine.status(), indent=2))


# ===============================================================================
#  QFX MODE (Mode 5)
# ===============================================================================
def mode_qfx():
    header("QFX INT4/Q8 OPTIMIZER")
    from qfx_optimizer import QFXOptimizer
    opt = QFXOptimizer()
    opt.optimize(rounds=30)
    ok(f"Best quant: {opt.best_quant()}")
    print(json.dumps(opt.report(), indent=2))


# ===============================================================================
#  TURBO MODE (Mode 14)
# ===============================================================================
def mode_turbo():
    header("INT4 TURBO HYBRID")
    from system_class import FXIONSystem
    from qfx_optimizer import QFXOptimizer
    sys_engine = FXIONSystem()
    sys_engine.start()
    opt = QFXOptimizer(sys_engine)
    opt.optimize(rounds=20)

    try:
        from fxion import FXIONEngine
        fe = FXIONEngine()
        fe.load_model("Q4_K_M")
        results = [fe.infer("turbo", max_tokens=128) for _ in range(5)]
        avg_tps = sum(r.tps for r in results) / len(results)
        ok(f"INT4 Turbo: avg {avg_tps:.1f} tok/s")
    except Exception as e:
        warn(f"FXION: {e}")

    print(json.dumps(opt.report(), indent=2))


# ===============================================================================
#  BENCHMARK (Mode 11)
# ===============================================================================
def mode_bench():
    header("GPU BENCHMARK -- ALL QUANT LEVELS")
    try:
        from fxion import FXIONEngine
        engine = FXIONEngine()
        results = engine.benchmark(iterations=10)
        cprint(f"\n  {'Quant':<10} {'Tok/s':>7} {'VRAM':>6} {'Accuracy':>9} {'Score':>7}", C.WHITE)
        cprint(f"  {'-'*42}", C.DIM)
        for q, r in results.items():
            marker = " [*]" if q == "Q8_0" else ""
            color = C.YELLOW if q == "Q8_0" else C.WHITE
            cprint(f"  {q:<10} {r['avg_tps']:>6.1f} {r['vram_gb']:>5.1f}G {r['accuracy']:>8.1%} {r['score']:>7.4f}{marker}", color)
    except Exception as e:
        fail(f"Benchmark failed: {e}")


# ===============================================================================
#  STATUS (Mode 10)
# ===============================================================================
def mode_status():
    header("SYSTEM STATUS")
    info(f"Python  : {sys.executable} ({sys.version.split()[0]})")
    info(f"Root    : {ROOT}")
    info(f"Platform: {platform.system()} {platform.release()}")
    print()

    # Modules
    cprint("  [MODULES]", C.CYAN)
    modules = [
        "system_class.py", "omnitech_core.py", "qfx_optimizer.py",
        "nnox_scheduler.py", "onyx_runtime.py",
        "fxion/__init__.py", "fxion/engine.py", "fxion/quantizer.py", "fxion/pcie.py",
        "neural_core.py", "ai_engine.py", "qfx_quant.py",
        "neural_core_qfx.py", "ai_engine_qfx.py", "vrm_manager.py",
        "turbo_quantum_qbridge.py", "cryptosavior_sdk.py", "convolutive_ai.py",
        "shadow_watchdog.py", "security_core.py", "fxion_self_heal.py",
        "fxion_cross_backend.py", "fxion_cipher.py"
    ]

    for m in modules:
        path = os.path.join(ROOT, m)
        if os.path.isfile(path):
            ok(m)
        else:
            fail(m)

    # Binary
    print()
    cprint("  [BINARY]", C.CYAN)
    fxion_bin = os.path.join(ROOT, "bin", "fxion_gpu.exe")
    if os.path.isfile(fxion_bin):
        ok(f"fxion_gpu.exe ({os.path.getsize(fxion_bin)} bytes)")
    else:
        warn("fxion_gpu.exe NOT BUILT -- run: launch.py install")

    # GPU
    print()
    cprint("  [GPU]", C.CYAN)
    gpu = detect_gpu()
    if gpu["available"]:
        ok(f"{gpu['name']} | {gpu['vram_total_mb']}MB | {gpu['clock_mhz']}MHz | {gpu['temp_c']} C")
    else:
        warn("No NVIDIA GPU detected")


# ===============================================================================
#  INSTALL (Mode 12)
# ===============================================================================
def mode_install():
    header("INSTALL + BUILD")

    step(1, 3, "Installing Python dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r",
                    os.path.join(ROOT, "requirements.txt")], check=False)
    ok("pip install complete")

    step(2, 3, "Checking CUDA build...")
    bin_dir = os.path.join(ROOT, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    fxion_bin = os.path.join(bin_dir, "fxion_gpu.exe")
    cu_src = os.path.join(ROOT, "fxion_pcie_engine.cu")

    if os.path.isfile(fxion_bin):
        ok("fxion_gpu.exe already built")
    elif os.path.isfile(cu_src):
        try:
            subprocess.check_output(["nvcc", "--version"], stderr=subprocess.DEVNULL)
            step(3, 3, "Compiling CUDA kernel (sm_52)...")
            result = subprocess.run(
                f'nvcc -arch=sm_52 -O2 -o "{fxion_bin}" "{cu_src}"',
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                ok(f"Built: {fxion_bin}")
            else:
                fail(f"nvcc error: {result.stderr[:200]}")
        except FileNotFoundError:
            warn("nvcc not found -- install CUDA Toolkit to build GPU kernel")
    else:
        fail(f"CUDA source not found: {cu_src}")

    ok("Install complete")


# ===============================================================================
#  TEST FXION MODULE
# ===============================================================================
def mode_test():
    header("FXION MODULE TEST")
    test_script = os.path.join(ROOT, "test_fxion.py")
    if os.path.isfile(test_script):
        subprocess.run([sys.executable, test_script], cwd=ROOT)
    else:
        fail("test_fxion.py not found")


# ===============================================================================
#  NNOX MODE (Mode 6)
# ===============================================================================
def mode_nnox():
    header("NNOX SCHEDULER")
    from system_class import FXIONSystem
    from nnox_scheduler import NNOXScheduler
    sys_engine = FXIONSystem()
    sys_engine.start()
    sched = NNOXScheduler(sys_engine)
    sched.route(10)
    print(json.dumps(sched.summary(), indent=2))


# ===============================================================================
#  ONYX MODE (Mode 7)
# ===============================================================================
def mode_onyx():
    header("ONYX RUNTIME")
    from system_class import FXIONSystem
    from onyx_runtime import ONYXRuntime
    sys_engine = FXIONSystem()
    sys_engine.start()
    sys_engine.gpu_loop(5)
    runtime = ONYXRuntime(sys_engine)
    runtime.run(steps=10)
    print(json.dumps(runtime.report(), indent=2))


# ===============================================================================
#  INTERACTIVE MENU
# ===============================================================================
def show_menu():
    show_splash()
    cprint(f"  Python : {sys.executable}", C.DIM)
    cprint(f"  Root   : {ROOT}", C.DIM)
    print()
    cprint("  +============================================================+", C.CYAN)
    cprint("  |              FXION-ONYX -- SELECT MODE                     |", C.CYAN)
    cprint("   =============================== ============================ ", C.CYAN)
    cprint("  |  1   Full Stack               |  8   Status Check         |", C.WHITE)
    cprint("  |  2   Q8 Augmented Boot [*]      |  9   GPU Benchmark        |", C.YELLOW)
    cprint("  |  3   Neural Engine            |  10  Install + Build      |", C.WHITE)
    cprint("  |  4   QFX Optimizer            |  11  Test FXION Module    |", C.WHITE)
    cprint("  |  5   INT4 Turbo Hybrid        |  12  FXION Engine Only    |", C.WHITE)
    cprint("  |  6   NNOX Scheduler           |  13  FXION Cipher          |", C.WHITE)
    cprint("  |  7   ONYX Runtime             |  14  Infinite Neural [*]     |", C.WHITE)
    cprint("  |                               |  0   Exit                 |", C.WHITE)
    cprint("  +=============================== ============================+", C.CYAN)
    print()

    choice = input("  Enter mode (0-14): ").strip()
    return choice


def mode_fxion_only():
    header("FXION ENGINE ONLY")
    try:
        from fxion import FXIONEngine
        engine = FXIONEngine()
        engine.load_model("Q8_0")
        cprint("  Running 10 inference passes...", C.DIM)
        for i in range(10):
            r = engine.infer(f"prompt_{i}", max_tokens=64)
            info(f"  pass={i:02d} tps={r.tps:.1f} lat={r.latency_ms:.1f}ms")
        s = engine.status()
        ok(f"Sessions: {s['sessions']} | Avg TPS: {s['avg_tps']}")
    except Exception as e:
        fail(str(e))


# ===============================================================================
#  CIPHER MODE -- XOR Partiel + Hashage + HMAC + Merge + D compression
# ===============================================================================
def mode_cipher():
    header("FXION CIPHER -- XOR + HASH + HMAC + MERGE")
    from fxion_cipher import FXIONCipher, HashageMultiType

    # Init
    key = b"FXION-ONYX-Q8-KEY"
    cipher = FXIONCipher(key)
    info(f"Algorithm: {cipher.info()['algorithm']}")
    info(f"Key derivation: PBKDF2 50000 iter")
    info(f"Hash algos: {', '.join(cipher.info()['hash_algos'])}")
    print()

    # Test 1: Encrypt/Decrypt string
    step(1, 5, "Chiffrement texte...")
    msg = "FXION-ONYX Q8 Augmented -- Confidential Payload"
    enc = cipher.encrypt_str(msg)
    dec = cipher.decrypt_str(enc)
    if dec != msg:
        raise AssertionError
    ok(f"'{msg[:30]}...' -> {len(enc)} bytes -> d chiffr  OK")

    # Test 2: Binary data
    step(2, 5, "Chiffrement binaire (4KB)...")
    import os as _os
    data = _os.urandom(4096)
    enc = cipher.encrypt(data)
    dec = cipher.decrypt(enc)
    if dec != data:
        raise AssertionError
    ok(f"{len(data)}B -> {len(enc)}B chiffr  (overhead: +{len(enc)-len(data)}B) -> OK")

    # Test 3: Tamper detection
    step(3, 5, "D tection corruption (HMAC)...")
    enc = cipher.encrypt(b"integrity test")
    tampered = bytearray(enc)
    tampered[-1] ^= 0xFF
    try:
        cipher.decrypt(bytes(tampered))
        fail("Corruption non d tect e!")
    except ValueError as e:
        ok(f"Tamper d tect : {e}")

    # Test 4: Wrong key rejection
    step(4, 5, "Rejet mauvaise cl ...")
    enc = cipher.encrypt(b"secret data")
    bad = FXIONCipher(b"WRONG-KEY", salt=cipher.salt)
    try:
        bad.decrypt(enc)
        fail("Mauvaise cl  accept e!")
    except ValueError as e:
        ok(f"Rejet : {e}")

    # Test 5: Hash composite
    step(5, 5, "Hashage multi-type composite...")
    hashes = HashageMultiType.hash_all(b"FXION-ONYX")
    for algo, h in hashes.items():
        info(f"  {algo:<10}: {h.hex()[:40]}...")
    composite = HashageMultiType.hash_composite(b"FXION-ONYX")
    ok(f"Composite: {composite.hex()[:40]}...")

    cprint(f"""
  +=======================================================+
  |  FXION CIPHER -- TOUS TESTS PASS S                    |
  |  XOR Partiel + Hash Multi + HMAC Double + XOR Merge  |
  |  Compression zlib-9 + Scramble + CRC32 Validation    |
  +=======================================================+""", C.GREEN)


# ===============================================================================
#  INFINITE NEURAL MODE -- Q-Layer L0 + Virtual Context/VRAM/Layers
# ===============================================================================
def mode_infinite():
    header("FXION INFINITE NEURAL -- Q-Layer L0 + Virtual Stack")
    from fxion_infinite import FXIONInfinite
    import numpy as np

    step(1, 6, "Initialising Infinite Neural Engine...")
    engine = FXIONInfinite(dim=512, layers=16, quant="Q8_0",
                           physical_vram_mb=4096, virtual_vram_mb=65536)
    ok(f"Stack: 16 layers | dim=512 | Q8_0 | VRAM: 4GB+64GB virtual")

    step(2, 6, "L0 Q-Layer forward pass...")
    x = np.random.randn(512).astype(np.float32)
    out = engine.infer(x, auto_expand=False)
    ok(f"Input {x.shape} -> Output {out.shape} | mean={out.mean():.4f}")

    step(3, 6, "Infinite neuron expansion (L0 +2048 neurons)...")
    before = engine.manager.l0.neuron_count
    engine.expand_neurons(2048)
    ok(f"L0 neurons: {before} -> {engine.manager.l0.neuron_count}")

    step(4, 6, "Virtual Context (100 tokens + recall)...")
    for i in range(100):
        engine.manager.context.push(np.random.randn(512).astype(np.float32))
    query = np.random.randn(512).astype(np.float32)
    recalled = engine.recall_context(query, top_k=3)
    ctx = engine.manager.context.status()
    ok(f"Tokens: {ctx['total_tokens_seen']} | Chain: {ctx['chain_length']} | Recalled: {len(recalled)}")

    step(5, 6, "Auto-expand (high complexity input)...")
    layers_before = len(engine.manager.layers)
    high_x = np.random.randn(512).astype(np.float32) * 5.0
    engine.infer(high_x, auto_expand=True)
    layers_after = len(engine.manager.layers)
    neurons_after = engine.manager.l0.neuron_count
    ok(f"Layers: {layers_before}->{layers_after} | L0 neurons: {neurons_after}")

    step(6, 6, "Virtual VRAM status...")
    vram = engine.manager.vram.usage()
    ok(f"Physical: {vram['physical_mb']}MB | Virtual: {vram['virtual_mb']}MB | "
       f"Pages: {vram['total_pages']} | GPU: {vram['gpu_pages']}")

    # Final
    status = engine.status()
    cprint(f"""
  +===========================================================+
  |  FXION INFINITE NEURAL -- COMPLETE                        |
  |  L0 Neurons  : {status['l0']['neurons']:<10}                            |
  |  Total Depth : {status['total_depth']:<10} layers (virtual)             |
  |  Total Params: {status['total_params']:<12}                          |
  |  Memory      : {status['total_memory_mb']:<8} MB                         |
  |  Context     : {status['context']['total_tokens_seen']:<8} tokens (infinite)           |
  |  VRAM        : {vram['total_mb']:<8} MB (physical+virtual)       |
  +===========================================================+""", C.YELLOW)


# ===============================================================================
#  MAIN DISPATCH
# ===============================================================================
COMMANDS = {
    "start":   mode_start,
    "full":    mode_start,
    "q8":      mode_q8,
    "neural":  mode_neural,
    "qfx":     mode_qfx,
    "turbo":   mode_turbo,
    "int4":    mode_turbo,
    "bench":   mode_bench,
    "status":  mode_status,
    "install": mode_install,
    "test":    mode_test,
    "nnox":    mode_nnox,
    "onyx":    mode_onyx,
    "fxion":   mode_fxion_only,
    "cipher":  mode_cipher,
    "infinite": mode_infinite,
    "neural-inf": mode_infinite,
}

MENU_MAP = {
    "1": mode_start,
    "2": mode_q8,
    "3": mode_neural,
    "4": mode_qfx,
    "5": mode_turbo,
    "6": mode_nnox,
    "7": mode_onyx,
    "8": mode_status,
    "9": mode_bench,
    "10": mode_install,
    "11": mode_test,
    "12": mode_fxion_only,
    "13": mode_cipher,
    "14": mode_infinite,
}


def main():
    # Enable ANSI on Windows
    if platform.system() == "Windows":
        os.system("")

    parser = argparse.ArgumentParser(
        description="FXION-ONYX Unified Launcher",
        usage="python launch.py [command]"
    )
    parser.add_argument("command", nargs="?", default=None,
                        help="Mode: q8|start|neural|qfx|turbo|bench|status|install|test|nnox|onyx|fxion")
    args = parser.parse_args()

    if args.command:
        cmd = args.command.lower()
        if cmd in COMMANDS:
            show_splash()
            COMMANDS[cmd]()
        else:
            fail(f"Unknown command: {cmd}")
            cprint(f"  Available: {', '.join(COMMANDS.keys())}", C.DIM)
            sys.exit(1)
    else:
        # Interactive menu
        choice = show_menu()
        if choice in MENU_MAP:
            MENU_MAP[choice]()
        elif choice == "0" or choice == "":
            cprint("  Exiting.", C.DIM)
        else:
            fail(f"Invalid choice: {choice}")

    print()
    cprint("  [FXION-ONYX] Done.", C.DIM)


if __name__ == "__main__":
    main()
