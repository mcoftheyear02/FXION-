# FXION-ONYX · OMNITECH Q8 Engine — PRD

## Original Problem Statement
> "BUILD THIS TO EXPERIMENTAL QINT COMPRESSION EN INT2 ZTDS EN ENTROPIE DYNAMIQUE XOR ET ALGEBRIQUE
> MATHEMATHIQUE ALGORITHM X/Y/Z AXIAL ELLIPTIQUE CYBERSECURITY CONFIGURATION NEURONBRIDGE
> CONFIGURATION QUANTUM ENTROPIE CRYPTOGRAPHIQUE EXPERIMENTAL COMPRESSION ALGORTIHM"
>
> Source artefact: `FXION-ONYX-final-MERGED-IQ.zip` (Python Q8 Augmented Quantization Engine + NeuronBridge 8.712 Quantum Genesis config).

## Architecture
- **Backend** FastAPI (`/app/backend/server.py`) wrapping the FXION-ONYX Python modules in `/app/backend/fxion/`:
  - Original: `system_class`, `qfx_optimizer`, `nnox_scheduler`, `onyx_runtime`, `core/qfx_quant`
  - **New experimental**: `qint_int2` (INT2 2-bit weight compression), `ztds_entropy` (XOR + GF(2⁸) algebraic stream), `xyz_elliptic` (secp256k1 tri-axial ECDH), `quantum_entropy` (SHA3-512 sponge + Von-Neumann debias), `neuron_bridge` (parses `neuronbridge.cfg`)
- **Frontend** React Command Center (`/app/frontend/src/App.js`) — dark amber-on-black cyberpunk dashboard, JetBrains Mono, Recharts (Radar + Bar + Line), live module status pills.
- **Storage** MongoDB collection `fxion_runs` (event history of resets and pipeline runs).

## API surface (`/api`)
- `GET /` · `GET /manifest` · `GET /system/status`
- `POST /system/gpu-loop` · `POST /system/reset`
- `POST /qfx/optimize` · `GET /qfx/profiles`
- `POST /nnox/route` · `POST /onyx/run`
- `POST /qint/compress` · `POST /ztds/encrypt`
- `GET  /xyz/handshake` · `POST /xyz/sign`
- `GET  /neuronbridge/config` · `GET /neuronbridge/summary`
- `POST /quantum/entropy`
- `POST /pipeline/run-all` (unified pipeline) · `GET /pipeline/history`

## Implemented (2026-01-16)
- 11/11 FXION modules wired into FastAPI and exposed.
- 5 NEW experimental modules added per the French/English brief (QINT INT2, ZTDS XOR + algebraic, X/Y/Z axial elliptic, NeuronBridge config loader, Quantum cryptographic entropy).
- Command Center UI with 12 panels, live charts, run-all pipeline, MongoDB-persisted history.
- End-to-end validated via curl + Playwright screenshots — pipeline executes in ~0.6s, every module reports.

## Backlog / Next
- P1: live WebSocket telemetry stream (replace polling).
- P1: CUDA kernel (`fxion_pcie_engine.cu`) build & invocation when GPU available.
- P2: persist QFX bandit state to MongoDB across restarts.
- P2: dashboard mode-selector (14 PowerShell modes — q8, neural, qfx, turbo, bench, scan, status, safe, api, docker, rebuild, install, menu, start).
- P3: import the original HTML dashboards (`omnitech_q8_dashboard.html`) as a "legacy" tab.

## Test Credentials
N/A — no auth in this build (all endpoints are open command surface).
