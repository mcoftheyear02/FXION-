#!/usr/bin/env bash
set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   FXION-ONYX  ·  OMNITECH Q8 ENGINE          ║"
echo "╚══════════════════════════════════════════════╝"

PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
  echo "[ERROR] Python not found. Install Python 3.10+"; exit 1
fi

MODE=${1:-q8}

case "$MODE" in
  q8)
    echo "[BOOT] Q8 Augmented Quantization"
    $PYTHON omnitech_core.py --qfx --quant Q8_0
    ;;
  neural)
    echo "[BOOT] Neural Baseline (FP32)"
    $PYTHON omnitech_core.py --neural
    ;;
  qfx)
    echo "[BOOT] QFX Optimizer"
    $PYTHON qfx_optimizer.py
    ;;
  bench)
    echo "[BENCH] Quantization Benchmark"
    $PYTHON -c "
from system_class import FXIONSystem
s = FXIONSystem()
s.start()
s.run_benchmark()
"
    ;;
  install)
    echo "[INSTALL] Installing dependencies..."
    pip install -r requirements.txt
    if command -v nvcc &>/dev/null; then
      echo "[CUDA] Compiling fxion_pcie_engine.cu..."
      nvcc -O3 -arch=sm_52 fxion_pcie_engine.cu -o fxion_pcie_engine
      echo "[CUDA] Done."
    else
      echo "[WARN] nvcc not found — skipping CUDA build."
    fi
    ;;
  *)
    echo "[ERROR] Unknown mode: $MODE"
    echo "Usage: ./run.sh [q8|neural|qfx|bench|install]"
    exit 1
    ;;
esac
