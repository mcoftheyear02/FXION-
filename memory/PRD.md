# FXION-ONYX · OMNITECH Q8 Engine — PRD (Jan 17 2026)

## Original Problem Statement
> Source: `FXION-ONYX-final-MERGED-IQ.zip` (Q8 Augmented Quantization Engine + NeuronBridge 8.712).
> Iterative extensions: QINT INT2/4/8, ZTDS XOR + algebraic entropy, X/Y/Z axial elliptic ECDH, NeuronBridge config, quantum entropy, QI per-layer, Deep-Learn SDK, elliptic seismograph, HARD compression w/ XOR prefetch hash chain, HyperLearn epoch XOR-on-success, CUDA fxion_pcie_engine.cu + OBTERON9 QLOGIC solver, Quant Fusion (3 merged lanes), Co-training AVX512 ↔ Cortex A72, HyperLearn PRIMARY L06→L12 IQ2_XS, real-time live polling, snapshots.

## 19 Modules wired end-to-end
| # | Module | Endpoint | Key fact |
|---|---|---|---|
| 1 | system_class | /system/status | UCB1 Q8 augmented policy |
| 2 | qfx_optimizer | /qfx/optimize | INT4/Q8/IQ adaptive bandit |
| 3 | nnox_scheduler | /nnox/route | GPU/CPU/Hybrid routing |
| 4 | onyx_runtime | /onyx/run | Live inference loop |
| 5 | qint_int2 | /qint/compress | 10.67× compression, 94% acc |
| 6 | ztds_entropy | /ztds/encrypt + /ztds/deep | XOR + GF(2⁸) algebraic stream |
| 7 | xyz_elliptic | /xyz/handshake | secp256k1 tri-axial ECDH |
| 8 | quantum_entropy | /quantum/entropy | SHA3-512 sponge + Von-Neumann |
| 9 | neuron_bridge | /neuronbridge/* | 8.712 Quantum Genesis cfg loader |
| 10 | qi_neuronbridge | /qi/neuronbridge | Per-layer ψ-coherence |
| 11 | deep_learn_sdk | /deep/forward | Dynamic entropic graph, GELU |
| 12 | elliptic_seismo | /elliptic/seismo | Lissajous wave + SHA3 signature |
| 13 | hard_compress | /hard/roundtrip | RLE→XOR→DEFLATE→BLAKE2b chain |
| 14 | qint_levels | /qint/bench-all | INT2/INT4/INT8 bench |
| 15 | hyperlearn | /hyperlearn/run + /compare | AVX512 vs Cortex A72 (3.76× speedup) |
| 16 | pcie_cuda | /pcie/run + /pcie/source | 12L×12B UCB1 OBTERON9 solver |
| 17 | qfusion | /qfusion/merge | INT_K_ALL · IQ_XS_ALL · M_XSM_NL_HYBRID |
| 18 | cotrain | /cotrain/run | AVX512 ↔ Cortex A72 XOR peer-sync + PCIe IQ4_NL override |
| 19 | hyperlearn_primary | /hyperlearn/primary | L06→L12 IQ2_XS, XOR mask 0x5A |

## Connected pipeline
- `POST /api/pipeline/run-all` exécute les 19 modules en ~0.75s, retourne JSON unifié.
- Frontend `runAll()` dispatch automatiquement chaque sous-objet vers son panel.
- 19/19 module pills emerald après Run Full Stack.

## Real-time + Snapshots
- `GET /api/live/tick` polled every 3s when LIVE toggle = ON.
- `POST /api/snapshot/save` persists full pipeline state in MongoDB `fxion_snapshots`.
- Click any snapshot tile to restore dashboard state.

## Architecture
- Backend: FastAPI + Motor (MongoDB) + numpy.
- Frontend: React + Recharts + lucide-react + Tailwind.
- Storage: MongoDB collections `fxion_runs`, `fxion_snapshots`.

## CUDA build (when GPU available)
`nvcc -arch=sm_52 -O3 -DFXION_PCIE_STANDALONE fxion/fxion_pcie_engine.cu -o bin/fxion_pcie_v2`

## Pending
- P0: Bitcoin wallet clarification (testnet vs mainnet read-only vs transactional) — user has not answered 1/2/3/STOP.
- P1: WebSocket replace 3s polling.
- P1: Interactive layer-range + quant sliders in HyperLearn Primary panel.
- P2: 14-mode selector (q8/neural/turbo/bench/scan/safe/docker/rebuild).

## Test Credentials
N/A — no auth.
