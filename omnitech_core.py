
"""
OMNITECH CORE — Master Orchestrator
Supports: --neural  (run neural engine)
          --qfx     (run INT4/Q8 quantized engine)
          (no flag) (run full system)
"""
import sys, argparse, logging
from system_class import FXIONSystem
from qfx_optimizer import QFXOptimizer
from nnox_scheduler import NNOXScheduler
from onyx_runtime import ONYXRuntime

log = logging.getLogger("OMNITECH_CORE")

def build_args():
    p = argparse.ArgumentParser(description="OMNITECH Core Orchestrator")
    p.add_argument("--neural", action="store_true", help="Neural engine mode")
    p.add_argument("--qfx",    action="store_true", help="QFX INT4/Q8 mode")
    p.add_argument("--iters",  type=int, default=20, help="GPU loop iterations")
    p.add_argument("--status", action="store_true", help="Print status and exit")
    return p.parse_args()

def run_neural(sys_engine: FXIONSystem):
    log.info("=== NEURAL ENGINE MODE ===")
    sys_engine.start()
    sys_engine.gpu_loop(iterations=15)
    log.info(f"Neural best quant: {sys_engine.policy.best()}")

def run_qfx(sys_engine: FXIONSystem):
    log.info("=== QFX INT4/Q8 ENGINE MODE ===")
    sys_engine.start()
    opt = QFXOptimizer(sys_engine)
    opt.optimize(rounds=10)
    log.info(f"QFX best quant: {opt.best_quant()}")

def run_full(sys_engine: FXIONSystem, iters: int):
    log.info("=== FULL STACK MODE ===")
    sys_engine.start()

    # 1. QFX pass
    opt = QFXOptimizer(sys_engine)
    opt.optimize(rounds=8)

    # 2. NNOX routing
    sched = NNOXScheduler(sys_engine)
    sched.route()

    # 3. ONYX runtime
    runtime = ONYXRuntime(sys_engine)
    runtime.run(steps=iters)

    log.info(f"Full stack best: {sys_engine.policy.best()}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format="[%(asctime)s] %(name)s %(levelname)s — %(message)s")

    args = build_args()
    engine = FXIONSystem()

    if args.status:
        import json
        engine.start()
        print(json.dumps(engine.status(), indent=2))
        sys.exit(0)
    elif args.neural:
        run_neural(engine)
    elif args.qfx:
        run_qfx(engine)
    else:
        run_full(engine, args.iters)

    print("\n=== OMNITECH STATUS ===")
    import json
    print(json.dumps(engine.status(), indent=2))
