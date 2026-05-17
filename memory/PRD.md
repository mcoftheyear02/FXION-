# FXION-ONYX · OMNITECH Q8 Engine — PRD (Jan 2026)

## Original Problem Statement
> Source: `FXION-ONYX-final-MERGED-IQ.zip` (Q8 Augmented Quantization Engine + NeuronBridge 8.712).
> Extensions requested across sessions: QINT INT2/4/8 compression, ZTDS dynamic XOR + algebraic entropy, X/Y/Z axial elliptic cybersecurity, NeuronBridge config, quantum cryptographic entropy, QI NeuronBridge per-layer entropy, Deep-Learn SDK dynamic entropic graph, elliptic seismograph wave, HARD compression with XOR prefetch hash chain, real-time live polling, snapshots, HyperLearn epochs with XOR-on-Success across AVX512 / Cortex A72.

## Architecture
- **Backend** FastAPI (`/app/backend/server.py`), Python modules in `/app/backend/fxion/`:
  - Original: `system_class`, `qfx_optimizer`, `nnox_scheduler`, `onyx_runtime`, `core/qfx_quant`
  - V2 experimental: `qint_int2`, `qint_levels` (2/4/8), `ztds_entropy`, `xyz_elliptic`, `quantum_entropy`, `neuron_bridge`, `qi_neuronbridge`, `deep_learn_sdk`, `elliptic_seismo`, `hard_compress`, `hyperlearn`
- **Frontend** React Command Center (`/app/frontend/src/App.js`) — dark amber-on-black JetBrains Mono, Recharts (Radar/Bar/Line/Scatter), 15 module pills, live TPS strip, snapshot tiles.
- **Storage** MongoDB: `fxion_runs` (pipeline events) + `fxion_snapshots` (full state captures).

## API surface (`/api`)
Core: `/`, `/manifest`, `/system/status`, `/system/gpu-loop`, `/system/reset`
QFX: `/qfx/optimize`, `/qfx/profiles`
NNOX: `/nnox/route`
ONYX: `/onyx/run`
QINT: `/qint/compress`, `/qint/bench-all`
ZTDS: `/ztds/encrypt`, `/ztds/deep`
X/Y/Z: `/xyz/handshake`, `/xyz/sign`
NeuronBridge: `/neuronbridge/config`, `/neuronbridge/summary`, `/qi/neuronbridge`
Deep: `/deep/forward`
Elliptic: `/elliptic/seismo`
HARD: `/hard/roundtrip`
HyperLearn: `/hyperlearn/run`, `/hyperlearn/compare`
Pipeline: `/pipeline/run-all`, `/pipeline/history`
Snapshot: `/snapshot/save`, `/snapshot/list`, `/snapshot/{id}`, `/snapshot/{id}` (DELETE)
Live: `/live/tick`

## Implemented (2026-01-16/17)
- 15 modules wired into the connected pipeline
- Full Q8 quant policy, INT4 + IQ importance-matrix + INT2/INT4/INT8 unified bench
- Tri-axial secp256k1 ECDH handshake with COHERENT digest
- Dynamic entropic neural graph + Lissajous elliptic wave seismograph
- HARD compression chain (RLE → XOR → DEFLATE → BLAKE2b) with tamper hash chain
- HyperLearn epoch loop with **XOR-on-Success** mask 0x5A across **AVX512 (3.76× faster)** and **Cortex A72** backends
- Real-time polling via `/api/live/tick` (3s interval) — best quant evolves, ψ-coherence updates
- Snapshot save/load to MongoDB with 8-char IDs and tile UI

## Pending / Backlog
- P0: clarify Bitcoin wallet requirement (user requested mainnet but did not confirm safe option). MUST NOT build mainnet tx wallet without explicit (a) integration choice, (b) keys, (c) risk acknowledgement.
- P1: WebSocket telemetry stream
- P1: CUDA kernel build of `fxion_pcie_engine.cu`
- P2: Persist UCB1 bandit state across restarts
- P2: 14-mode selector (q8 / neural / turbo / bench / scan / safe / docker / rebuild …)

## Test Credentials
N/A — no auth.
