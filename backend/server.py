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
    elapsed = round(time.time() - t0, 3)
    result = {
        "elapsed_s": elapsed,
        "ts": datetime.now(timezone.utc).isoformat(),
        "system_status": ENGINE.status(),
        "qfx": opt.report(),
        "nnox": sched.summary(),
        "onyx": rt.report(),
        "qint_int2": qint,
        "ztds": ztds,
        "xyz_elliptic": xyz,
        "quantum_entropy": qe,
        "neuron_bridge": nb,
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
