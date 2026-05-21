# FXION-ONYX — OMNITECH Q8 Augmented Quantization Engine
> Autonomous RL-driven quantization optimizer for LLMs on GTX 970 / any CUDA GPU.

---

## Quick Start

### Windows (PowerShell)
```powershell
cd FXION-ONYX-FINAL
.\omnitech.ps1             # interactive 14-mode menu
.\omnitech.ps1 q8          # ★ Q8 Augmented Boot (recommended)
.\omnitech.ps1 install     # install Python deps + build CUDA
.\omnitech.ps1 bench       # GPU benchmark all quant levels
```

### Linux / macOS
```bash
chmod +x run.sh && ./run.sh          # full stack
python omnitech_core.py --qfx        # Q8 augmented mode
python omnitech_core.py --neural     # neural baseline
```

---

## Folder Structure
```
FXION-ONYX-FINAL/
├── omnitech.ps1            ← 14-mode master driver (PowerShell)
├── omnitech_core.py        ← main orchestrator (--neural / --qfx)
├── system_class.py         ← FXIONSystem engine + UCB1 policy
├── qfx_optimizer.py        ← QFX RL optimizer + Q8 bandit
├── nnox_scheduler.py       ← NNOX neural routing scheduler
├── onyx_runtime.py         ← ONYX runtime loop
├── fxion_pcie_engine.cu    ← CUDA Q8 matmul kernel
├── run.sh                  ← Linux/macOS launcher
├── requirements.txt        ← Python dependencies
├── docker-compose.yml      ← Docker stack (API + Redis)
├── dashboard/
│   ├── omnitech_q8_dashboard.html  ← Q8 Command Center UI
│   └── omnitech_dashboard.html     ← Original dashboard
└── core/
    ├── neural_core.py       ← FP32 baseline neural engine
    ├── neural_core_qfx.py   ← INT4/Q8 quantized engine
    ├── ai_engine.py         ← FP32 inference coordinator
    ├── ai_engine_qfx.py     ← Q8 inference coordinator
    └── qfx_quant.py         ← INT8/INT4 quantization library
```

---

## 14 Modes
| Flag       | Mode                         | Description                        |
|------------|------------------------------|------------------------------------|
| `q8`       | Q8 Augmented Boot            | 7-stage Q8 init + UCB1 policy      |
| `start`    | Full Stack                   | All engines + API server           |
| `neural`   | Neural Baseline              | FP32 neural engine only            |
| `qfx`      | QFX Engine                   | INT4/Q8 optimizer only             |
| `turbo`    | INT4 Turbo Hybrid            | Max tokens/sec mode                |
| `bench`    | GPU Benchmark                | Full quant level benchmark table   |
| `install`  | Install + Build              | pip install + nvcc compile         |
| `scan`     | Drive Scan                   | Reconstruct from all drives        |
| `status`   | Health Check                 | Module + GPU status table          |
| `safe`     | Safe Extreme Mode            | Guarded extreme performance        |
| `api`      | API Server Only              | Flask REST API on :9000            |
| `docker`   | Docker Stack                 | Start full Docker compose stack    |
| `rebuild`  | Master Rebuild               | 5-stage reconstruct pipeline       |
| `menu`     | Interactive Menu             | Numbered mode selector             |

---

## Q8 Augmented Quantization
- **UCB1 bandit policy** — C=1.414, Q8_0 prior boost +0.12
- **Block size**: 32 weights per scale factor
- **VRAM budget**: 3.82 / 4.00 GB (GTX 970)
- **Target throughput**: 128.4 tok/s @ 1550MHz locked
- **Accuracy**: 99.1% vs FP32 baseline (Q8_0 MAE < 0.0008)

---

## Requirements
- Python 3.10+
- NVIDIA GPU (GTX 970 or better), CUDA 11+
- Redis (for RL history persistence)
- numpy, flask, redis-py

## License
MIT — OMNITECH / FXION-ONYX Project
