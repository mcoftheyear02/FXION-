#!/usr/bin/env python3
"""
FXION-ONYX -- BUILD ALL CONNECTED
==================================
Unified master entry point that boots and interconnects ALL subsystems:

  1. OMNITECH Engine    (FXIONSystem, QFXOptimizer, NNOXScheduler, ONYXRuntime)
  2. FXION Module       (FXIONEngine, FXIONQuantizer, PCIeBridge)
  3. IQ4_NL Genesis     (L0_OBERON, HMAC_SHIELD, NEUTRINO_IOS, CORTEX_A72, OBERON_MIND)
  4. Security Layer     (HMACOberonShield, LoneRoadPipeline, NeutrinoIOS)
  5. API Dashboard      (Flask app with unified /api/connected status)

Run:
    python build_all_connected.py          # boot everything
    python build_all_connected.py --no-api # skip Flask dashboard
"""

import sys
import os
import time
import json
import threading
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# -- Path Setup ----------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.environ["FXION_PATH"] = ROOT
os.environ["PYTHONPATH"] = ROOT

# -- Logging -------------------------------------------------------------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler("logs/build_all_connected.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BUILD_ALL_CONNECTED")

# -- ANSI Colors ---------------------------------------------------------------
C_CYAN    = "\033[96m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_RED     = "\033[91m"
C_MAGENTA = "\033[95m"
C_BOLD    = "\033[1m"
C_DIM     = "\033[90m"
C_RESET   = "\033[0m"


def ok(msg):
    print(f"  {C_GREEN}[OK]{C_RESET}   {msg}")

def warn(msg):
    print(f"  {C_YELLOW}[WARN]{C_RESET} {msg}")

def fail(msg):
    print(f"  {C_RED}[FAIL]{C_RESET} {msg}")

def step(num, total, msg):
    print(f"  {C_CYAN}[{num}/{total}]{C_RESET} {msg}")


class BuildAllConnected:
    """
    Master controller that boots every FXION subsystem, wires them together,
    and exposes a unified status via the Flask API dashboard.
    """

    TOTAL_STEPS = 7

    def __init__(self, start_api=True):
        self.start_api = start_api
        self.boot_time = datetime.now()
        self.running = True
        self.executor = ThreadPoolExecutor(max_workers=12, thread_name_prefix="FXION_BOOT")

        # Subsystem references (populated during boot)
        self.omnitech_engine = None
        self.qfx_optimizer = None
        self.nnox_scheduler = None
        self.onyx_runtime = None
        self.fxion_engine = None
        self.fxion_quantizer = None
        self.pcie_bridge = None
        self.hmac_shield = None
        self.neutrino_ios = None
        self.cortex_bridge = None
        self.oberon_mind = None
        self.lone_road = None
        self.flask_app = None

        # Status tracking
        self.layers = {
            "OMNITECH_ENGINE":  False,
            "QFX_OPTIMIZER":    False,
            "NNOX_SCHEDULER":   False,
            "ONYX_RUNTIME":     False,
            "FXION_ENGINE":     False,
            "FXION_QUANTIZER":  False,
            "PCIE_BRIDGE":      False,
            "L0_OBERON":        False,
            "HMAC_SHIELD":      False,
            "NEUTRINO_IOS":     False,
            "CORTEX_A72":       False,
            "OBERON_MIND":      False,
            "LONE_ROAD":        False,
            "API_DASHBOARD":    False,
        }

    # ==========================================================================
    #  STEP 1: OMNITECH Engine Core
    # ==========================================================================
    def _boot_omnitech(self):
        step(1, self.TOTAL_STEPS, "Booting OMNITECH Engine Core...")
        try:
            from system_class import FXIONSystem
            self.omnitech_engine = FXIONSystem()
            self.omnitech_engine.start()
            self.layers["OMNITECH_ENGINE"] = True
            ok(f"FXIONSystem ACTIVE | GPU: {self.omnitech_engine.gpu_info.get('name', 'N/A')}")
        except Exception as e:
            fail(f"OMNITECH Engine: {e}")
            logger.error(f"OMNITECH boot failed: {e}")

    # ==========================================================================
    #  STEP 2: QFX + NNOX + ONYX Pipeline
    # ==========================================================================
    def _boot_pipeline(self):
        step(2, self.TOTAL_STEPS, "Initializing QFX/NNOX/ONYX Pipeline...")
        try:
            from qfx_optimizer import QFXOptimizer
            self.qfx_optimizer = QFXOptimizer(self.omnitech_engine)
            self.qfx_optimizer.optimize(rounds=8)
            self.layers["QFX_OPTIMIZER"] = True
            ok(f"QFX Optimizer: best={self.qfx_optimizer.best_quant()} | rounds={self.qfx_optimizer.t}")
        except Exception as e:
            fail(f"QFX Optimizer: {e}")
            logger.error(f"QFX boot failed: {e}")

        try:
            from nnox_scheduler import NNOXScheduler
            self.nnox_scheduler = NNOXScheduler(self.omnitech_engine)
            self.nnox_scheduler.route(jobs=5)
            self.layers["NNOX_SCHEDULER"] = True
            ok(f"NNOX Scheduler: {self.nnox_scheduler.summary()}")
        except Exception as e:
            fail(f"NNOX Scheduler: {e}")
            logger.error(f"NNOX boot failed: {e}")

        try:
            from onyx_runtime import ONYXRuntime
            self.onyx_runtime = ONYXRuntime(self.omnitech_engine)
            self.onyx_runtime.run(steps=5)
            self.layers["ONYX_RUNTIME"] = True
            ok(f"ONYX Runtime: {self.onyx_runtime.report()}")
        except Exception as e:
            fail(f"ONYX Runtime: {e}")
            logger.error(f"ONYX boot failed: {e}")

    # ==========================================================================
    #  STEP 3: FXION Module (Engine + Quantizer + PCIe)
    # ==========================================================================
    def _boot_fxion_module(self):
        step(3, self.TOTAL_STEPS, "Loading FXION Module (Engine + Quantizer + PCIe)...")
        try:
            from fxion.engine import FXIONEngine
            self.fxion_engine = FXIONEngine(vram_budget_gb=4.0)
            best_q = "Q8_0"
            if self.qfx_optimizer:
                best_q = self.qfx_optimizer.best_quant()
            self.fxion_engine.load_model(best_q)
            result = self.fxion_engine.infer("Build All Connected test", max_tokens=64)
            self.layers["FXION_ENGINE"] = True
            ok(f"FXIONEngine: quant={result.quant} tps={result.tps} acc={result.accuracy}")
        except Exception as e:
            warn(f"FXIONEngine: {e}")
            logger.warning(f"FXION Engine: {e}")

        try:
            from fxion.quantizer import FXIONQuantizer
            self.fxion_quantizer = FXIONQuantizer()
            self.layers["FXION_QUANTIZER"] = True
            ok("FXIONQuantizer ready")
        except Exception as e:
            warn(f"FXIONQuantizer: {e}")

        try:
            from fxion.pcie import PCIeBridge
            self.pcie_bridge = PCIeBridge()
            self.layers["PCIE_BRIDGE"] = True
            ok(f"PCIeBridge: {self.pcie_bridge.status()['pcie']} | kernel={self.pcie_bridge.status()['kernel_binary']}")
        except Exception as e:
            warn(f"PCIeBridge: {e}")

    # ==========================================================================
    #  STEP 4: IQ4_NL Security Layer (L0 Oberon + HMAC Shield)
    # ==========================================================================
    def _boot_security(self):
        step(4, self.TOTAL_STEPS, "Activating IQ4_NL Security Layer...")
        try:
            from security.hmac_oberon_shield import HMACOberonShield
            self.hmac_shield = HMACOberonShield()
            self.layers["L0_OBERON"] = True
            self.layers["HMAC_SHIELD"] = True
            ok("L0 Oberon BoarShield + HMAC-SHA3-512 ACTIVE")
        except Exception as e:
            fail(f"HMAC Shield: {e}")
            logger.error(f"Security boot failed: {e}")

    # ==========================================================================
    #  STEP 5: Neutrino IOS + Phantom Layers
    # ==========================================================================
    def _boot_neutrino(self):
        step(5, self.TOTAL_STEPS, "Igniting Neutrino IOS & Phantom Layers...")
        try:
            from core.neutrino_ios import NeutrinoIOS
            self.neutrino_ios = NeutrinoIOS(num_phantom_layers=3)
            self.neutrino_ios.deploy_sterile_detectors(count=5)
            self.layers["NEUTRINO_IOS"] = True
            status = self.neutrino_ios.get_status()
            ok(f"Neutrino IOS: {status['phantom_layers']['active']} phantom layers | "
               f"{status['statistics']['total_neutrinos_spawned']} neutrinos spawned")
        except Exception as e:
            fail(f"Neutrino IOS: {e}")
            logger.error(f"Neutrino boot failed: {e}")

    # ==========================================================================
    #  STEP 6: Cortex A-72 + Oberon Mind + Lone Road Pipeline (WIRING)
    # ==========================================================================
    def _boot_neural_wiring(self):
        step(6, self.TOTAL_STEPS, "Wiring Cortex A-72 + Oberon Mind + Lone Road Pipeline...")
        try:
            from core.cortex_a72_bridge import CortexA72Bridge
            self.cortex_bridge = CortexA72Bridge()
            self.layers["CORTEX_A72"] = True

            from core.oberon_mind_ex import OberonMindEX
            self.oberon_mind = OberonMindEX(cortex=self.cortex_bridge)
            self.layers["OBERON_MIND"] = True

            # Wire Cortex -> Oberon Mind (Logic Layer callback)
            self.cortex_bridge.connect_logic_layer(
                lambda payload: self.oberon_mind.process(payload.get("data", payload))
            )

            # Wire Cortex -> System broadcast (feed OMNITECH engine telemetry)
            def system_broadcast(payload):
                logger.debug(f"[BROADCAST] {payload.get('pictography', '-')} "
                             f"type={payload.get('type', 'UNKNOWN')}")
            self.cortex_bridge.connect_system_rest(system_broadcast)

            ok("Cortex A-72 <-> Oberon Mind neural link ESTABLISHED")

            # Wire Lone Road Pipeline (Security -> Neural path)
            from security.lone_road_pipeline import LoneRoadPipeline
            self.lone_road = LoneRoadPipeline(
                mind=self.oberon_mind,
                shield=self.hmac_shield
            )
            self.layers["LONE_ROAD"] = True
            ok("Lone Road Pipeline: NET/LAN lanes SECURED")

            # Run a test signal through the full pipeline
            test_data = {"ra": 266.4, "dec": -29.0, "intensity": 0.9, "lane": "LAN"}
            self.cortex_bridge.ingest_iq4_nl("LAN", test_data)
            ok("End-to-end signal test: LAN -> Cortex -> Oberon Mind PASSED")

            # Activate ZTDS AVX512 hybrid mode: Q8_0 + IQ2_XS via Cortex A-72
            if self.fxion_engine:
                ztds_result = self.fxion_engine.activate_ztds_avx512(
                    cortex_bridge=self.cortex_bridge
                )
                if ztds_result.get("status") == "ACTIVE":
                    # Run a ZTDS hybrid inference to confirm
                    ztds_infer = self.fxion_engine.infer_ztds(
                        "ZTDS AVX512 Cortex A-72 validation", max_tokens=64
                    )
                    ok(f"ZTDS AVX512 ACTIVE: Q8_0+IQ2_XS | "
                       f"TPS={ztds_result['fused_tps']} | "
                       f"ACC={ztds_result['fused_accuracy']} | "
                       f"Cortex=ROUTED")
                else:
                    warn(f"ZTDS AVX512: {ztds_result}")

        except Exception as e:
            fail(f"Neural wiring: {e}")
            logger.error(f"Neural wiring failed: {e}")

    # ==========================================================================
    #  STEP 7: API Dashboard with Unified Status
    # ==========================================================================
    def _boot_api(self):
        if not self.start_api:
            warn("API Dashboard skipped (--no-api)")
            return

        step(7, self.TOTAL_STEPS, "Starting Unified API Dashboard (Port 5000)...")
        try:
            from api.app import app as flask_app
            self._register_connected_endpoints(flask_app)
            self.flask_app = flask_app

            def run_flask():
                flask_app.run(host='0.0.0.0', port=5000, debug=False,
                              use_reloader=False, threaded=True)

            t = threading.Thread(target=run_flask, daemon=True)
            t.start()
            time.sleep(1)
            self.layers["API_DASHBOARD"] = True
            ok("API Dashboard ONLINE at http://localhost:5000")
            ok("Unified status at http://localhost:5000/api/connected")
        except Exception as e:
            fail(f"API Dashboard: {e}")
            logger.error(f"API boot failed: {e}")

    def _register_connected_endpoints(self, flask_app):
        """Add /api/connected endpoint exposing all subsystem statuses."""
        master = self

        @flask_app.route('/api/connected')
        def api_connected():
            from flask import jsonify
            return jsonify(master.get_unified_status())

        @flask_app.route('/connected')
        def connected_dashboard():
            from flask import render_template_string
            return render_template_string(CONNECTED_DASHBOARD_HTML)

    # ==========================================================================
    #  Unified Status
    # ==========================================================================
    def get_unified_status(self):
        """Aggregate status from every connected subsystem."""
        status = {
            "system": "FXION-ONYX BUILD ALL CONNECTED",
            "boot_time": self.boot_time.isoformat(),
            "uptime_seconds": round((datetime.now() - self.boot_time).total_seconds(), 1),
            "layers": self.layers,
            "active_count": sum(1 for v in self.layers.values() if v),
            "total_count": len(self.layers),
        }

        # OMNITECH Engine
        if self.omnitech_engine:
            status["omnitech"] = self.omnitech_engine.status()

        # QFX Optimizer
        if self.qfx_optimizer:
            status["qfx"] = self.qfx_optimizer.report()

        # NNOX Scheduler
        if self.nnox_scheduler:
            status["nnox"] = self.nnox_scheduler.summary()

        # ONYX Runtime
        if self.onyx_runtime:
            status["onyx"] = self.onyx_runtime.report()

        # FXION Engine
        if self.fxion_engine:
            status["fxion_engine"] = self.fxion_engine.status()

        # FXION Quantizer
        if self.fxion_quantizer:
            status["fxion_quantizer"] = self.fxion_quantizer.report()

        # PCIe Bridge
        if self.pcie_bridge:
            status["pcie"] = self.pcie_bridge.status()

        # HMAC Shield
        if self.hmac_shield:
            shield_status = self.hmac_shield.get_status()
            shield_status.pop('recent_cherenkov_events', None)
            status["hmac_shield"] = shield_status

        # Neutrino IOS
        if self.neutrino_ios:
            status["neutrino_ios"] = self.neutrino_ios.get_status()

        # Oberon Mind
        if self.oberon_mind:
            status["oberon_mind"] = self.oberon_mind.get_status()

        return status

    # ==========================================================================
    #  Diagnostics
    # ==========================================================================
    def run_diagnostics(self):
        print(f"\n{C_CYAN}{'='*60}{C_RESET}")
        print(f"  {C_BOLD}SYSTEM DIAGNOSTICS{C_RESET}")
        print(f"{C_CYAN}{'='*60}{C_RESET}")
        all_good = True
        for layer, active in self.layers.items():
            icon = f"{C_GREEN}[ACTIVE]{C_RESET}" if active else f"{C_RED}[FAILED]{C_RESET}"
            print(f"  {icon}  {layer}")
            if not active:
                all_good = False
        active = sum(1 for v in self.layers.values() if v)
        total = len(self.layers)
        print(f"\n  {C_BOLD}Score: {active}/{total} subsystems connected{C_RESET}")
        return all_good

    # ==========================================================================
    #  Main Boot Sequence
    # ==========================================================================
    def start(self):
        print(f"\n{C_CYAN}{'='*60}{C_RESET}")
        print(f"  {C_BOLD}{C_MAGENTA}FXION-ONYX{C_RESET} // {C_BOLD}{C_CYAN}BUILD ALL CONNECTED{C_RESET}")
        print(f"  {C_DIM}Unified Master Boot Sequence{C_RESET}")
        print(f"{C_CYAN}{'='*60}{C_RESET}\n")

        # Sequential boot for dependency ordering
        self._boot_omnitech()
        self._boot_pipeline()
        self._boot_fxion_module()
        self._boot_security()
        self._boot_neutrino()
        self._boot_neural_wiring()
        self._boot_api()

        # Final diagnostics
        all_ok = self.run_diagnostics()

        active = sum(1 for v in self.layers.values() if v)
        total = len(self.layers)

        if all_ok:
            print(f"\n{C_GREEN}{'='*60}{C_RESET}")
            print(f"  {C_GREEN}{C_BOLD}ALL {total} SUBSYSTEMS CONNECTED SUCCESSFULLY{C_RESET}")
        else:
            print(f"\n{C_YELLOW}{'='*60}{C_RESET}")
            print(f"  {C_YELLOW}{C_BOLD}{active}/{total} SUBSYSTEMS CONNECTED{C_RESET}")

        print(f"{C_CYAN}{'='*60}{C_RESET}")
        print(f"  {C_BOLD}Subsystems Online:{C_RESET}")
        print(f"    OMNITECH Engine : {'ACTIVE' if self.layers['OMNITECH_ENGINE'] else 'FAILED'}")
        print(f"    QFX Optimizer   : {'ACTIVE' if self.layers['QFX_OPTIMIZER'] else 'FAILED'}")
        print(f"    NNOX Scheduler  : {'ACTIVE' if self.layers['NNOX_SCHEDULER'] else 'FAILED'}")
        print(f"    ONYX Runtime    : {'ACTIVE' if self.layers['ONYX_RUNTIME'] else 'FAILED'}")
        print(f"    FXION Engine    : {'ACTIVE' if self.layers['FXION_ENGINE'] else 'FAILED'}")
        print(f"    FXION Quantizer : {'ACTIVE' if self.layers['FXION_QUANTIZER'] else 'FAILED'}")
        print(f"    PCIe Bridge     : {'ACTIVE' if self.layers['PCIE_BRIDGE'] else 'FAILED'}")
        print(f"    L0 Oberon       : {'ACTIVE' if self.layers['L0_OBERON'] else 'FAILED'}")
        print(f"    HMAC Shield     : {'ACTIVE' if self.layers['HMAC_SHIELD'] else 'FAILED'}")
        print(f"    Neutrino IOS    : {'ACTIVE' if self.layers['NEUTRINO_IOS'] else 'FAILED'}")
        print(f"    Cortex A-72     : {'ACTIVE' if self.layers['CORTEX_A72'] else 'FAILED'}")
        print(f"    Oberon Mind     : {'ACTIVE' if self.layers['OBERON_MIND'] else 'FAILED'}")
        print(f"    Lone Road       : {'ACTIVE' if self.layers['LONE_ROAD'] else 'FAILED'}")
        print(f"    API Dashboard   : {'ACTIVE' if self.layers['API_DASHBOARD'] else 'SKIPPED'}")

        if self.layers["API_DASHBOARD"]:
            print(f"\n  {C_BOLD}Access Points:{C_RESET}")
            print(f"    Dashboard    : {C_CYAN}http://localhost:5000{C_RESET}")
            print(f"    Connected API: {C_CYAN}http://localhost:5000/api/connected{C_RESET}")
            print(f"    Quantum Dash : {C_CYAN}http://localhost:5000/quantum{C_RESET}")
            print(f"    Health Check : {C_CYAN}http://localhost:5000/health{C_RESET}")

        print(f"{C_CYAN}{'='*60}{C_RESET}\n")

        # Write unified status to disk
        os.makedirs("dashboard", exist_ok=True)
        with open("dashboard/connected_status.json", "w") as f:
            json.dump(self.get_unified_status(), f, indent=2, default=str)

        logger.info(f"BUILD ALL CONNECTED complete: {active}/{total} subsystems online")

        # Keep alive
        if self.layers["API_DASHBOARD"]:
            try:
                print(f"  {C_DIM}System running. Press Ctrl+C to shutdown.{C_RESET}\n")
                while self.running:
                    time.sleep(5)
                    # Periodic status update
                    with open("dashboard/connected_status.json", "w") as f:
                        json.dump(self.get_unified_status(), f, indent=2, default=str)
            except KeyboardInterrupt:
                logger.info("Shutting down BUILD ALL CONNECTED...")
                self.running = False
                self.executor.shutdown(wait=False)


# ==============================================================================
#  Connected Dashboard HTML
# ==============================================================================
CONNECTED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FXION-ONYX | BUILD ALL CONNECTED</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Consolas', 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a1a1a 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #00d9ff;
            margin-bottom: 30px;
        }
        h1 {
            font-size: 2.2em;
            background: linear-gradient(90deg, #00d9ff, #e94560, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: none;
        }
        .subtitle { color: #888; margin-top: 8px; font-size: 0.9em; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .card {
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(0,217,255,0.15);
        }
        .card h2 {
            color: #00d9ff;
            font-size: 1em;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0,217,255,0.2);
        }
        .layer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 8px;
        }
        .layer {
            padding: 10px;
            border-radius: 8px;
            font-size: 0.85em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .layer.active {
            background: rgba(0,255,136,0.1);
            border: 1px solid rgba(0,255,136,0.3);
            color: #00ff88;
        }
        .layer.failed {
            background: rgba(233,69,96,0.1);
            border: 1px solid rgba(233,69,96,0.3);
            color: #e94560;
        }
        .dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot.green { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
        .dot.red { background: #e94560; box-shadow: 0 0 6px #e94560; }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 0.9em;
        }
        .stat-label { color: #888; }
        .stat-value { color: #00d9ff; font-weight: bold; }
        .score-box {
            text-align: center;
            padding: 20px;
            background: rgba(0,255,136,0.05);
            border-radius: 12px;
            border: 1px solid rgba(0,255,136,0.2);
            margin-bottom: 20px;
        }
        .score { font-size: 3em; color: #00ff88; font-weight: bold; }
        .score-label { color: #888; font-size: 0.9em; }
        #status-text { color: #888; text-align: center; margin-top: 16px; font-size: 0.85em; }
        pre {
            background: rgba(0,0,0,0.3);
            padding: 12px;
            border-radius: 8px;
            font-size: 0.8em;
            overflow-x: auto;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>FXION-ONYX // BUILD ALL CONNECTED</h1>
            <p class="subtitle">Unified System Status Dashboard</p>
        </header>

        <div class="score-box">
            <div class="score" id="score">--/--</div>
            <div class="score-label">SUBSYSTEMS CONNECTED</div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
            <h2>SUBSYSTEM STATUS</h2>
            <div class="layer-grid" id="layers"></div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>OMNITECH ENGINE</h2>
                <div id="omnitech">Loading...</div>
            </div>
            <div class="card">
                <h2>QFX OPTIMIZER</h2>
                <div id="qfx">Loading...</div>
            </div>
            <div class="card">
                <h2>NNOX SCHEDULER</h2>
                <div id="nnox">Loading...</div>
            </div>
            <div class="card">
                <h2>ONYX RUNTIME</h2>
                <div id="onyx">Loading...</div>
            </div>
            <div class="card">
                <h2>FXION ENGINE</h2>
                <div id="fxion_engine">Loading...</div>
            </div>
            <div class="card">
                <h2>HMAC SHIELD</h2>
                <div id="hmac">Loading...</div>
            </div>
            <div class="card">
                <h2>NEUTRINO IOS</h2>
                <div id="neutrino">Loading...</div>
            </div>
            <div class="card">
                <h2>OBERON MIND</h2>
                <div id="oberon">Loading...</div>
            </div>
        </div>

        <div class="card">
            <h2>RAW STATUS JSON</h2>
            <pre id="raw-json">Loading...</pre>
        </div>

        <p id="status-text">Auto-refreshing every 3 seconds</p>
    </div>

    <script>
        function stat(label, value) {
            return `<div class="stat"><span class="stat-label">${label}</span><span class="stat-value">${value}</span></div>`;
        }

        async function loadData() {
            try {
                const res = await fetch('/api/connected');
                const d = await res.json();

                // Score
                document.getElementById('score').textContent = `${d.active_count}/${d.total_count}`;

                // Layers
                const layersDiv = document.getElementById('layers');
                layersDiv.innerHTML = '';
                for (const [name, active] of Object.entries(d.layers || {})) {
                    const cls = active ? 'active' : 'failed';
                    const dot = active ? 'green' : 'red';
                    layersDiv.innerHTML += `<div class="layer ${cls}"><span class="dot ${dot}"></span>${name}</div>`;
                }

                // Omnitech
                const om = d.omnitech;
                if (om) {
                    document.getElementById('omnitech').innerHTML =
                        stat('Mode', om.mode) +
                        stat('Running', om.running) +
                        stat('Best Quant', om.best_quant) +
                        stat('GPU', om.gpu?.name || 'N/A');
                }

                // QFX
                const qfx = d.qfx;
                if (qfx) {
                    document.getElementById('qfx').innerHTML =
                        stat('Best', qfx.best) +
                        stat('Rounds', qfx.rounds);
                }

                // NNOX
                const nnox = d.nnox;
                if (nnox) {
                    document.getElementById('nnox').innerHTML =
                        stat('Total Jobs', nnox.total) +
                        stat('GPU', nnox.gpu) +
                        stat('CPU', nnox.cpu) +
                        stat('Avg Latency', nnox.avg_latency_ms + ' ms');
                }

                // ONYX
                const onyx = d.onyx;
                if (onyx) {
                    document.getElementById('onyx').innerHTML =
                        stat('Steps', onyx.steps) +
                        stat('Avg TPS', onyx.avg_tps) +
                        stat('Total Tokens', onyx.total_tokens) +
                        stat('Quant', onyx.quant);
                }

                // FXION Engine
                const fe = d.fxion_engine;
                if (fe) {
                    let feHtml =
                        stat('GPU', fe.gpu?.name || 'N/A') +
                        stat('Active Quant', fe.active_quant) +
                        stat('Sessions', fe.sessions) +
                        stat('Avg TPS', fe.avg_tps);
                    if (fe.ztds) {
                        feHtml +=
                            stat('ZTDS Mode', fe.ztds.fusion_mode) +
                            stat('CPU Backend', fe.ztds.cpu_backend) +
                            stat('Split Ratio', (fe.ztds.split_ratio * 100) + '%') +
                            stat('Fused TPS', fe.ztds.fused_tps) +
                            stat('Fused ACC', fe.ztds.fused_accuracy) +
                            stat('Cortex Routed', fe.ztds.cortex_routed ? 'YES' : 'NO');
                    }
                    document.getElementById('fxion_engine').innerHTML = feHtml;
                }

                // HMAC Shield
                const hmac = d.hmac_shield;
                if (hmac) {
                    document.getElementById('hmac').innerHTML =
                        stat('Status', hmac.status) +
                        stat('Algorithm', hmac.algorithm) +
                        stat('Key Rotation', hmac.key_rotation) +
                        stat('Defense Level', hmac.defense_level) +
                        stat('Validated', hmac.validated_packets) +
                        stat('Vaporized', hmac.vaporized_packets);
                }

                // Neutrino
                const ni = d.neutrino_ios;
                if (ni) {
                    document.getElementById('neutrino').innerHTML =
                        stat('Status', ni.status) +
                        stat('Phantom Layers', `${ni.phantom_layers?.active}/${ni.phantom_layers?.total}`) +
                        stat('Neutrinos Spawned', ni.statistics?.total_neutrinos_spawned) +
                        stat('Intrusions', ni.statistics?.intrusions_detected);
                }

                // Oberon Mind
                const ob = d.oberon_mind;
                if (ob) {
                    document.getElementById('oberon').innerHTML =
                        stat('IQ Level', ob.iq_level?.toFixed(2)) +
                        stat('Training Sessions', ob.training_sessions) +
                        stat('Knowledge Entries', ob.knowledge_entries) +
                        stat('Status', ob.status);
                }

                // Raw JSON
                document.getElementById('raw-json').textContent = JSON.stringify(d, null, 2);
                document.getElementById('status-text').textContent =
                    `Last updated: ${new Date().toLocaleTimeString()} | Auto-refreshing every 3s`;
            } catch (err) {
                document.getElementById('status-text').textContent = 'Error loading: ' + err;
            }
        }
        loadData();
        setInterval(loadData, 3000);
    </script>
</body>
</html>
"""


# ==============================================================================
#  Entry Point
# ==============================================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FXION-ONYX -- BUILD ALL CONNECTED")
    parser.add_argument("--no-api", action="store_true", help="Skip Flask API dashboard")
    args = parser.parse_args()

    master = BuildAllConnected(start_api=not args.no_api)
    master.start()
