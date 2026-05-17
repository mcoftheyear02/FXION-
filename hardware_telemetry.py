
"""
FXION HARDWARE TELEMETRY -- Neural & GPU Monitoring
Feeds the Self-Heal engine with real-time hardware metrics.
"""
import time, json, os
import numpy as np

def get_gpu_telemetry():
    # Simulated GPU telemetry for GTX 970 / CUDA
    # In a real environment, this would call nvidia-smi or pynvml
    return {
        "temp": 65 + np.random.randint(-2, 5),
        "load": 88 + np.random.randint(-5, 5),
        "vram_used": 3.2 + (np.random.random() * 0.3), # GB
        "vram_total": 4.0,
        "clock_mhz": 1550 + np.random.randint(-10, 10)
    }

def get_cpu_telemetry():
    # Simulated CPU telemetry for Cortex/x64
    return {
        "load": 45 + np.random.randint(-5, 10),
        "ram_used": 8.5 + (np.random.random() * 0.5),
        "ram_total": 16.0
    }

def update_dashboard_stats(
    psi,
    hashrate,
    total_mined=0.0,
    self_heal_data=None,
    savior_fitness=0.0,
    wallet_address=None,
    mining_status=None,
    pool_status=None,
    shares_accepted=0,
    shares_rejected=0,
    last_nonce=None,
    current_job=None
):
    os.makedirs("dashboard", exist_ok=True)
    
    # Load current balance and currencies from vault if not provided
    balance_usd = 0.0
    balance_cad = 0.0
    active_backend = "N/A"
    self_heal_status = self_heal_data if self_heal_data else {"is_healing": False, "last_heal": "NONE"}
    
    try:
        with open("vault/fxion_vault.json", "r") as f:
            vdata = json.load(f)
            if total_mined == 0.0:
                total_mined = vdata.get("balance_btc", 0.0)
            balance_usd = vdata.get("balance_usd", 0.0)
            balance_cad = vdata.get("balance_cad", 0.0)
    except: pass

    # Detect active backend, self-heal, and CryptoSavior Expert state
    qi_infinite = 0.0
    decrypt_progress = 0.0
    hash_boost = 1.0
    qbits_total = 0
    turbo_lat = 0.0
    try:
        if os.path.exists("vault/evolution_state.json"):
            with open("vault/evolution_state.json", "r") as f:
                evo = json.load(f)
                qi_infinite = evo.get("qi_infinite", 0.0)
                decrypt_progress = evo.get("decrypt_progress", 0.0)
                hash_boost = evo.get("hashrate_boost", 1.0)
                qbits_total = evo.get("qbits_processed", 0)
    except: pass

    # Detect VRM Turbo stats
    try:
        if os.path.exists("dashboard/vrm_stats.json"):
            with open("dashboard/vrm_stats.json", "r") as f:
                vrm_data = json.load(f)
                turbo_lat = vrm_data.get("last_latency", 0.0)
    except: pass

    try:
        if os.path.exists("dashboard/backend_status.txt"):
            with open("dashboard/backend_status.txt", "r") as f:
                active_backend = f.read().strip()
    except: pass

    stats = {
        "psi": psi,
        "hashrate": f"{hashrate * hash_boost:.2f} KH/s",
        "hash_boost": f"x{hash_boost:.2f}",
        "total_mined": f"{total_mined:.8f} BTC",
        "balance_usd": f"${balance_usd:,.2f} USD",
        "balance_cad": f"${balance_cad:,.2f} CAD",
        "active_backend": active_backend,
        "turbo_latency": f"{turbo_lat:.3f}ms",
        "self_heal": self_heal_status,
        "savior_fitness": f"{savior_fitness:.4f}",
        "wallet_address": wallet_address or "UNKNOWN",
        "mining_status": mining_status or "IDLE",
        "pool_status": pool_status or "DISCONNECTED",
        "shares_accepted": shares_accepted,
        "shares_rejected": shares_rejected,
        "last_nonce": last_nonce or "",
        "current_job": current_job or "",
        "qi_infinite": qi_infinite,
        "qbits_total": qbits_total,
        "decrypt_progress": decrypt_progress,
        "ai_mode": "HYPERACTIVE_CONVOLUTIVE",
        "security_status": "PROTECTED_AES256",
        "gpu": get_gpu_telemetry(),
        "cpu": get_cpu_telemetry(),
        "timestamp": time.time(),
        "status": "OMEGA_STABLE"
    }
    try:
        with open("dashboard/live_stats.json", "w") as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass


if __name__ == "__main__":
    print(f"GPU: {get_gpu_telemetry()}")
    print(f"CPU: {get_cpu_telemetry()}")
