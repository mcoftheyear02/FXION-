[README.md](https://github.com/user-attachments/files/27574451/README.md)
# ⚡ OMNITECH OMEGA v3.0
### Autonomous AI Quantization Engine

> RL-driven quantization optimizer for LLMs — finds the optimal GGUF quantization level by maximizing tokens/sec, accuracy, and model size tradeoffs automatically.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OMNITECH OMEGA                        │
│                                                         │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │  Quantizer  │──▶│   Redis      │◀──│   Worker    │  │
│  │  RL (UCB1)  │   │  Job Queue   │   │ (llama.cpp) │  │
│  └─────────────┘   └──────────────┘   └─────────────┘  │
│         │                 │                   │         │
│         ▼                 ▼                   ▼         │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │  Policy     │   │  Scheduler   │   │  Security   │  │
│  │  (UCB1)     │   │  (gate)      │   │  AI         │  │
│  └─────────────┘   └──────────────┘   └─────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  API (Flask)  │  WebSocket  │  Nginx  │  Prometheus│  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📦 Components

| Component | Description |
|-----------|-------------|
| `core/quantizer_rl.py` | UCB1 bandit RL loop — selects, quantizes, benchmarks |
| `core/policy.py` | UCB1 policy with persistent state |
| `core/worker.py` | Multi-GPU llama.cpp benchmark runner |
| `core/scheduler.py` | Redis queue gate / job rate limiter |
| `core/dataset_eval.py` | Model accuracy evaluator |
| `api/app.py` | Flask REST API + live HTML dashboard |
| `api/stream_server.py` | WebSocket real-time stream |
| `security/security_ai.py` | Anomaly detection & alerting |
| `nginx/omnitech.conf` | Reverse proxy config |
| `monitoring/prometheus.yml` | Prometheus scrape config |

## 🚀 Quick Start

### Option 1 — Docker (recommended)
```bash
docker-compose up -d
open http://localhost:5000
```

### Option 2 — Bare metal
```bash
chmod +x run.sh
./run.sh
```

### Option 3 — Bootable ISO
```bash
chmod +x build_iso.sh
./build_iso.sh
# Flash omnitech-omega.iso to USB
```

## ⚙️ Configuration

Set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OMNITECH_BASE_MODEL` | `./models/mistral-7b.f16.gguf` | Path to base f16 GGUF |
| `OMNITECH_QUANT_BIN` | `./llama.cpp/quantize` | Path to quantize binary |
| `W_TPS` | `0.6` | TPS reward weight |
| `W_ACC` | `30.0` | Accuracy reward weight |
| `W_SIZE` | `0.01` | Size penalty weight |

## 🔌 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Live dashboard (HTML) |
| `GET /api/history` | Last 100 RL iterations |
| `GET /api/status` | System health & best quant |
| `GET /api/policy` | UCB1 policy state |
| `GET /health` | Redis & service health |
| `WS ws://localhost:8765` | Real-time streaming |

## 📊 Supported Quantizations

`Q2_K` → `Q3_K` → `Q4_K_M` → `Q5_K_M` → `Q6_K` → `Q8_0`

Lower = faster/smaller, Higher = more accurate. OMNITECH finds the sweet spot automatically.

---
*OMNITECH LEVEL 3 COMPLETE 🚀*
