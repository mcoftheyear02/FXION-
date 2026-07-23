#!/usr/bin/env python3
"""
FXION UNIFIED LOADER - Load All Modules
Version: 1.0.0
Loads and initializes all FXION system components
"""

import sys
import json
import logging
import os
from datetime import datetime

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/fxion_loader.log", mode="a")
    ]
)
log = logging.getLogger("FXION_LOADER")

# Module categories
MODULES = {
    "security": [
        "fxion_secure_vault",
        "secure_vault",
        "security_core",
        "fxion_cipher",
        "fxion_entropy_lock"
    ],
    "ai": [
        "ai_engine",
        "ai_engine_qfx",
        "neural_core",
        "neural_core_qfx",
        "convolutive_ai",
        "autotrain_fxion"
    ],
    "mining": [
        "bitcoin_miner_qfx",
        "gpu_stratum_miner",
        "fxion_real_mining_kernel",
        "mine_wallet",
        "fxion_wallet",
        "fxion_pool_connector"
    ],
    "core": [
        "FXION_MASTER_CONTROL",
        "FXION_ONYX_FINAL",
        "launch",
        "system_root",
        "system_class",
        "fxion_infinite"
    ],
    "support": [
        "onyx_qlayer",
        "nnox_scheduler",
        "fxion_self_heal",
        "cryptosavior_sdk",
        "shadow_watchdog",
        "hardware_telemetry",
        "phantom_memory",
        "qfx_optimizer",
        "fusion_engine_kv_optimized"
    ]
}


def load_module(mod_name):
    """Load a single module and return status."""
    try:
        mod = __import__(mod_name)
        file_size = len(open(f"{mod_name}.py").read())
        return {"status": "OK", "size": file_size}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def load_all():
    """Load all modules by category."""
    results = {"timestamp": datetime.now().isoformat(), "categories": {}}
    total_ok = 0
    total_error = 0
    
    print("\n" + "="*60)
    print("  FXION UNIFIED SYSTEM LOADER")
    print("  Loading all modules...")
    print("="*60 + "\n")
    
    for category, modules in MODULES.items():
        log.info(f"Loading {category.upper()} modules...")
        cat_results = {}
        
        for mod_name in modules:
            result = load_module(mod_name)
            cat_results[mod_name] = result
            
            if result["status"] == "OK":
                total_ok += 1
                print(f"  [OK] {mod_name} ({result['size']} bytes)")
            else:
                total_error += 1
                print(f"  [ERR] {mod_name}: {result.get('error', 'Unknown error')}")
        
        results["categories"][category] = cat_results
        ok_count = len([r for r in cat_results.values() if r['status']=='OK'])
        print(f"\n{category.upper()}: {ok_count}/{len(modules)} loaded")
    
    results["summary"] = {"total_ok": total_ok, "total_error": total_error}
    
    print("\n" + "="*60)
    print(f"  SUMMARY: {total_ok} OK | {total_error} ERRORS")
    print("="*60 + "\n")
    
    # Save report
    with open("logs/loader_report.json", "w") as f:
        json.dump(results, f, indent=2)
    log.info("Report saved to logs/loader_report.json")
    
    return results


if __name__ == "__main__":
    load_all()
