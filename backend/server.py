from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os, sys, logging, json, uuid, time
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Make FXION package importable
sys.path.insert(0, str(ROOT_DIR / 'fxion'))
sys.path.insert(0, str(ROOT_DIR / 'fxion' / 'core'))

# FXION-ONYX modules
from fxion.system_class import FXIONSystem, QUANTS
from fxion.qfx_optimizer import QFXOptimizer, QUANT_PROFILES
from fxion.nnox_scheduler import NNOXScheduler
from fxion.onyx_runtime import ONYXRuntime
from fxion import qint_int2, ztds_entropy, xyz_elliptic, neuron_bridge, quantum_entropy
from fxion import qint_levels, qi_neuronbridge, deep_learn_sdk, elliptic_seismo, hard_compress
from fxion import hyperlearn
from fxion import fxion_pcie_simulator
from fxion import qfusion

# MongoDB
mongo_url = os.environ['MONGO_URL']
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ['DB_NAME']]

app = FastAPI(title="FXION-ONYX Command API")
api = APIRouter(prefix="/api")

# Single shared FXION engine instance (in-process)
ENGINE = FXIONSystem()
ENGINE.start()

logging.basicConfig(level=logging.INFO,
    format='[%(asctime)s] %(name)s %(levelname)s - %(message)s')
log = logging.getLogger("FXION_API")


# ────────── Request models ──────────
class OptimizeReq(BaseModel):
    rounds: int = 12

class RouteReq(BaseModel):
    jobs: int = 8

class RuntimeReq(BaseModel):
    steps: int = 6

class EncryptReq(BaseModel):
    message: str
    key: Optional[str] = "FXION-ONYX-ZTDS-2026"

class CompressReq(BaseModel):
    size: int = 4096
    seed: int = 42

class EntropyReq(BaseModel):
    size: int = 1024


# ────────── Core ──────────
@api.get("/")
async def root():
    return {"service": "FXION-ONYX Command API", "version": "FINAL-Q8", "status": "online"}


@api.get("/manifest")
async def manifest():
    with open(ROOT_DIR / "fxion" / "manifest.json") as f:
        return json.load(f)


@api.get("/system/status")
async def system_status():
    return ENGINE.status()


@api.post("/system/gpu-loop")
async def gpu_loop(req: RuntimeReq):
    ENGINE.gpu_loop(iterations=max(1, min(req.steps, 50)))
    return {
        "ok": True,
        "best_quant": ENGINE.policy.best(),
        "history": ENGINE.history[-req.steps:],
        "policy": ENGINE.policy.summary(),
    }


@api.post("/system/reset")
async def system_reset():
    global ENGINE
    ENGINE = FXIONSystem()
    ENGINE.start()
    await db.fxion_runs.insert_one({
        "id": str(uuid.uuid4()),
        "event": "engine_reset",
        "ts": datetime.now(timezone.utc).isoformat(),
    })
    return {"ok": True, "status": ENGINE.status()}


# ────────── QFX Optimizer ──────────
@api.post("/qfx/optimize")
async def qfx_optimize(req: OptimizeReq):
    opt = QFXOptimizer(ENGINE)
    rounds = max(1, min(req.rounds, 60))
    opt.optimize(rounds=rounds)
    rep = opt.report()
    rep["log"] = opt.log
    await db.fxion_runs.insert_one({
        "id": str(uuid.uuid4()), "event": "qfx_optimize",
        "rounds": rounds, "best": rep["best"],
        "ts": datetime.now(timezone.utc).isoformat(),
    })
    return rep


@api.get("/qfx/profiles")
async def qfx_profiles():
    return {"profiles": QUANT_PROFILES}


# ────────── NNOX Scheduler ──────────
@api.post("/nnox/route")
async def nnox_route(req: RouteReq):
    sched = NNOXScheduler(ENGINE)
    sched.route(jobs=max(1, min(req.jobs, 40)))
    return {"summary": sched.summary(), "routes": sched.routes}


# ────────── ONYX Runtime ──────────
@api.post("/onyx/run")
async def onyx_run(req: RuntimeReq):
    rt = ONYXRuntime(ENGINE)
    rt.run(steps=max(1, min(req.steps, 30)))
    return {"report": rt.report(), "metrics": rt.metrics}


# ────────── Experimental: QINT INT2 ──────────
@api.post("/qint/compress")
async def qint_compress(req: CompressReq):
    rep = qint_int2.compress_report(size=max(64, min(req.size, 65536)), seed=req.seed)
    return rep


# ────────── ZTDS Dynamic Entropy XOR ──────────
@api.post("/ztds/encrypt")
async def ztds_encrypt(req: EncryptReq):
    if not req.message:
        raise HTTPException(400, "message required")
    return ztds_entropy.encrypt_demo(req.message, req.key)


# ────────── X/Y/Z Axial Elliptic Cybersecurity ──────────
@api.get("/xyz/handshake")
async def xyz_handshake():
    return xyz_elliptic.axial_handshake()


@api.post("/xyz/sign")
async def xyz_sign(req: EncryptReq):
    return xyz_elliptic.sign_payload(req.message)


# ────────── NeuronBridge config ──────────
@api.get("/neuronbridge/config")
async def nb_config():
    return neuron_bridge.load_config()


@api.get("/neuronbridge/summary")
async def nb_summary():
    return neuron_bridge.summary()


# ────────── Quantum Entropy ──────────
@api.post("/quantum/entropy")
async def quantum_entropy_report(req: EntropyReq):
    return quantum_entropy.report(size=max(64, min(req.size, 16384)))


# ────────── Unified pipeline ──────────
@api.post("/pipeline/run-all")
async def run_all():
    """Connect every module end-to-end and return a unified report."""
    t0 = time.time()
    opt = QFXOptimizer(ENGINE)
    opt.optimize(rounds=10)
    sched = NNOXScheduler(ENGINE)
    sched.route(jobs=6)
    rt = ONYXRuntime(ENGINE)
    rt.run(steps=5)
    qint = qint_int2.compress_report(size=4096)
    ztds = ztds_entropy.encrypt_demo("FXION-ONYX QUANTUM GENESIS PAYLOAD", "ZTDS-IQ-2026")
    xyz = xyz_elliptic.axial_handshake()
    qe = quantum_entropy.report(size=1024)
    nb = neuron_bridge.summary()
    # v2
    qint_bench = qint_levels.bench_all(size=4096)
    qi = qi_neuronbridge.layer_map()
    deep = deep_learn_sdk.run(nodes=16, steps=8)
    seismo = elliptic_seismo.wave(a=3.0, b=2.0, n=200)
    hard = hard_compress.roundtrip_demo()
    elapsed = round(time.time() - t0, 3)
    result = {
        "elapsed_s": elapsed,
        "ts": datetime.now(timezone.utc).isoformat(),
        "modules_count": 14,
        "system_status": ENGINE.status(),
        "qfx": opt.report(),
        "nnox": sched.summary(),
        "onyx": rt.report(),
        "qint_int2": qint,
        "ztds": ztds,
        "xyz_elliptic": xyz,
        "quantum_entropy": qe,
        "neuron_bridge": nb,
        "qint_bench": qint_bench,
        "qi_neuronbridge": {k: v for k, v in qi.items() if k != "layers"} | {"layers_sample": qi["layers"][:3]},
        "deep_learn_sdk": {k: v for k, v in deep.items() if k != "steps"} | {"steps_sample": deep["steps"][:3]},
        "elliptic_seismo": {k: v for k, v in seismo.items() if k not in ("x", "y")},
        "hard_compress": hard,
    }
    await db.fxion_runs.insert_one({
        "id": str(uuid.uuid4()), "event": "pipeline_run_all",
        "elapsed_s": elapsed, "best": opt.best_quant(),
        "ts": result["ts"],
    })
    return result


@api.get("/pipeline/history")
async def pipeline_history():
    rows = await db.fxion_runs.find({}, {"_id": 0}).sort("ts", -1).to_list(50)
    return {"history": rows}


# ────────── SNAPSHOTS ──────────
@api.post("/snapshot/save")
async def snapshot_save():
    """Capture full pipeline state and persist as a snapshot."""
    snap = await run_all()  # reuse the unified pipeline
    sid = str(uuid.uuid4())
    doc = {
        "id": sid,
        "ts": snap["ts"],
        "elapsed_s": snap["elapsed_s"],
        "best_quant": snap["qfx"]["best"],
        "modules_count": snap["modules_count"],
        "payload": snap,
    }
    await db.fxion_snapshots.insert_one(doc)
    return {"snapshot_id": sid, "ts": snap["ts"], "best_quant": snap["qfx"]["best"], "modules": snap["modules_count"]}


@api.get("/snapshot/list")
async def snapshot_list():
    rows = await db.fxion_snapshots.find(
        {}, {"_id": 0, "payload": 0}
    ).sort("ts", -1).to_list(50)
    return {"snapshots": rows}


@api.get("/snapshot/{sid}")
async def snapshot_get(sid: str):
    row = await db.fxion_snapshots.find_one({"id": sid}, {"_id": 0})
    if not row:
        raise HTTPException(404, "snapshot not found")
    return row


@api.delete("/snapshot/{sid}")
async def snapshot_delete(sid: str):
    r = await db.fxion_snapshots.delete_one({"id": sid})
    return {"deleted": r.deleted_count}


# ────────── REAL-TIME LIVE FEED ──────────
@api.get("/live/tick")
async def live_tick():
    """Lightweight tick endpoint for real-time polling."""
    # one quick UCB1 sample to evolve history
    arm = ENGINE.policy.select()
    quant = QUANTS[arm]
    tps = ENGINE._simulate_inference(quant)
    reward = ENGINE._compute_reward(quant, tps)
    ENGINE.policy.update(arm, reward)
    ENGINE.history.append({"iter": len(ENGINE.history), "quant": quant, "tps": round(tps, 1), "reward": round(reward, 4)})
    qi = qi_neuronbridge.layer_map()
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tick": {
            "iter": len(ENGINE.history) - 1,
            "quant": quant,
            "tps": round(tps, 1),
            "reward": round(reward, 4),
        },
        "best_quant": ENGINE.policy.best(),
        "qi_avg_coherence": qi["avg_coherence"],
        "qi_active": qi["active_layers"],
        "policy_summary": ENGINE.policy.summary(),
        "history_tail": ENGINE.history[-30:],
    }


# ────────── EXPERIMENTAL EXTENSIONS (v2) ──────────
class QintLevelReq(BaseModel):
    size: int = 8192


@api.post("/qint/bench-all")
async def qint_bench_all(req: QintLevelReq):
    return qint_levels.bench_all(size=max(256, min(req.size, 65536)))


@api.get("/qi/neuronbridge")
async def qi_bridge():
    return qi_neuronbridge.layer_map()


class DeepReq(BaseModel):
    nodes: int = 16
    steps: int = 8
    density: float = 0.35


@api.post("/deep/forward")
async def deep_forward(req: DeepReq):
    return deep_learn_sdk.run(nodes=req.nodes, steps=req.steps, density=req.density)


class WaveReq(BaseModel):
    a: float = 3.0
    b: float = 2.0
    delta: float = 0.7853981633974483
    n: int = 256
    noise: float = 0.02
    seed: int = 11


@api.post("/elliptic/seismo")
async def elliptic_seismo_endpoint(req: WaveReq):
    return elliptic_seismo.wave(a=req.a, b=req.b, delta=req.delta, n=req.n, noise=req.noise, seed=req.seed)


class HardReq(BaseModel):
    message: Optional[str] = None


@api.post("/hard/roundtrip")
async def hard_roundtrip(req: HardReq):
    return hard_compress.roundtrip_demo(req.message)


class ZtdsDeepReq(BaseModel):
    message: str
    rounds: int = 3
    key: Optional[str] = "FXION-ONYX-ZTDS-DEEP"


@api.post("/ztds/deep")
async def ztds_deep(req: ZtdsDeepReq):
    import hashlib as _h
    pt = req.message.encode("utf-8")
    ct = pt
    keys_used = []
    cur_key = req.key
    rounds = max(1, min(req.rounds, 8))
    for r in range(rounds):
        ct = ztds_entropy.encrypt(ct, cur_key)
        keys_used.append(_h.sha256(cur_key.encode()).hexdigest()[:12])
        cur_key = _h.sha256((cur_key + ":" + str(r)).encode()).hexdigest()
    # decrypt back
    dec_key = req.key
    dt = ct
    for r in range(rounds):
        dt = ztds_entropy.decrypt(dt, dec_key)
        dec_key = _h.sha256((dec_key + ":" + str(r)).encode()).hexdigest()
    return {
        "algorithm": "ZTDS Deep (chained rotating keys)",
        "rounds": rounds,
        "key_chain_preview": keys_used,
        "plaintext": req.message,
        "ciphertext_hex": ct.hex(),
        "decrypted": dt.decode("utf-8", errors="replace"),
        "match": dt == pt,
        "plaintext_entropy_bits": round(ztds_entropy.shannon_entropy(pt), 4),
        "ciphertext_entropy_bits": round(ztds_entropy.shannon_entropy(ct), 4),
    }


# ────────── HYPERLEARN · XOR-on-Success ──────────
class HyperReq(BaseModel):
    epochs: int = 30
    backend: str = "AVX512"
    lr: float = 0.04
    weight_dim: int = 512
    seed: int = 42


@api.post("/hyperlearn/run")
async def hyperlearn_run(req: HyperReq):
    return hyperlearn.run(
        epochs=max(4, min(req.epochs, 200)),
        backend=req.backend,
        lr=max(0.001, min(req.lr, 0.5)),
        weight_dim=max(32, min(req.weight_dim, 4096)),
        seed=req.seed,
    )


class HyperCompareReq(BaseModel):
    epochs: int = 30
    weight_dim: int = 512
    seed: int = 42


@api.post("/hyperlearn/compare")
async def hyperlearn_compare(req: HyperCompareReq):
    return hyperlearn.compare(
        epochs=max(4, min(req.epochs, 200)),
        weight_dim=max(32, min(req.weight_dim, 4096)),
        seed=req.seed,
    )


# ────────── FXION PCIe v2 · CUDA (mirrored on CPU) ──────────
class PcieReq(BaseModel):
    epochs: int = 256
    capture_every: int = 8


@api.post("/pcie/run")
async def pcie_run(req: PcieReq):
    return fxion_pcie_simulator.run(
        epochs=max(8, min(req.epochs, 2048)),
        capture_every=max(0, min(req.capture_every, 64)),
    )


@api.get("/pcie/source")
async def pcie_source():
    """Return the CUDA kernel source for inspection in the UI."""
    p = ROOT_DIR / "fxion" / "fxion_pcie_engine.cu"
    if not p.exists():
        raise HTTPException(404, "kernel source missing")
    src = p.read_text()
    return {
        "file": "fxion_pcie_engine.cu",
        "lines": src.count("\n"),
        "size_bytes": len(src),
        "build_command": "nvcc -arch=sm_52 -O3 -DFXION_PCIE_STANDALONE fxion_pcie_engine.cu -o fxion_pcie_v2",
        "kernels": ["ucb1_score_kernel", "obteron9_qlogic_kernel", "update_reward_kernel"],
        "topology": "12 layers × 12 bridges",
        "primary_quant": "IQ2_XS",
        "source_preview": src[:1800],
    }

# ────────── QUANT FUSION · merge lanes ──────────
@api.get("/qfusion/merge")
async def qfusion_merge():
    return qfusion.all_merges()





app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()
