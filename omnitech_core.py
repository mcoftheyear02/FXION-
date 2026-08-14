"""
OMNITECH CORE — Master Orchestrator

Supports: --neural  (run neural engine)
          --qfx     (run INT4/Q8 quantized engine)
          (no flag) (run full system)
"""
import argparse
import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qfx_optimizer import QFXOptimizer
    from nnox_scheduler import NNOXScheduler
    from onyx_runtime import ONYXRuntime

from system_class import FXIONSystem

log = logging.getLogger("OMNITECH_CORE")


def build_args() -> argparse.Namespace:
    """Build command-line argument parser.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="OMNITECH Core Orchestrator")
    parser.add_argument("--neural", action="store_true", help="Neural engine mode")
    parser.add_argument("--qfx", action="store_true", help="QFX INT4/Q8 mode")
    parser.add_argument("--iters", type=int, default=20, help="GPU loop iterations")
    parser.add_argument("--status", action="store_true", help="Print status and exit")
    return parser.parse_args()


def run_neural(sys_engine: FXIONSystem) -> None:
    """Run neural engine mode.

    Args:
        sys_engine: FXIONSystem instance
    """
    log.info("=== NEURAL ENGINE MODE ===")
    sys_engine.start()
    sys_engine.gpu_loop(iterations=15)
    log.info("Neural best quant: %s", sys_engine.policy.best())


def run_qfx(sys_engine: FXIONSystem) -> None:
    """Run QFX INT4/Q8 engine mode.

    Args:
        sys_engine: FXIONSystem instance
    """
    # Import here to avoid circular dependency
    from qfx_optimizer import QFXOptimizer

    log.info("=== QFX INT4/Q8 ENGINE MODE ===")
    sys_engine.start()
    opt = QFXOptimizer(sys_engine)
    opt.optimize(rounds=10)
    log.info("QFX best quant: %s", opt.best_quant())


def run_full(sys_engine: FXIONSystem, iters: int) -> None:
    """Run full stack mode.

    Args:
        sys_engine: FXIONSystem instance
        iters: Number of GPU loop iterations
    """
    # Import here to avoid circular dependency
    from qfx_optimizer import QFXOptimizer
    from nnox_scheduler import NNOXScheduler
    from onyx_runtime import ONYXRuntime

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

    log.info("Full stack best: %s", sys_engine.policy.best())


def print_status(engine: FXIONSystem) -> None:
    """Print system status as JSON.

    Args:
        engine: FXIONSystem instance
    """
    import json

    engine.start()
    print(json.dumps(engine.status(), indent=2))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s] %(name)s %(levelname)s — %(message)s"
    )

    args = build_args()
    engine = FXIONSystem()

    if args.status:
        print_status(engine)
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
