
"""
FXION MASTER LAUNCHER -- OMEGA UNIFIED STARTUP
1. Checks dependencies.
2. Starts the HUD Web Server.
3. Launches the Master Control Engine.
"""
import os, sys, subprocess, time, threading


# CYBERPUNK COLOR PALETTE (FXION)
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"
C_GOLD = "\033[93m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

def check_dependencies():
    print(f"{C_CYAN}[BIOS]{C_RESET} Probing DYSON NEURAL dependencies...")
    required_files = [
        "FXION_MASTER_CONTROL.py", "onyx_qlayer.py", "fxion_wallet.py",
        "fxion_pool_connector.py", "fxion_background_service.py",
        "hardware_telemetry.py", "phantom_memory.py", "qfx_optimizer.py",
        "fxion_hal.py", "bitcoin_miner_qfx.py", "fxion_omega_unified.cfg",
        "convolutive_ai.py", "shadow_watchdog.py", "security_core.py", "fxion_self_heal.py",
        "vrm_manager.py", "turbo_quantum_qbridge.py", "cryptosavior_sdk.py",
        "nnox_scheduler.py", "autotrain_fxion.py", "fxion_cross_backend.py", "fxion_cipher.py"
    ]
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print(f"{C_RED}[SUDO_ERR]{C_RESET} Neural Bridge Broken! Missing segments: {C_MAGENTA}{', '.join(missing)}{C_RESET}")
        return False
    
    try:
        import numpy
        import cryptography
    except ImportError as e:
        print(f"{C_RED}[SUDO_ERR]{C_RESET} SDK Missing: {C_GOLD}{e}{C_RESET}. Run: {C_CYAN}pip install numpy cryptography{C_RESET}")
        return False
    
    print(f"{C_GREEN}[BIOS]{C_RESET} All Dyson-Link layers verified. {C_CYAN}READY_FOR_BOOT.{C_RESET}")
    return True

def launch_hud():
    print(f"{C_MAGENTA}[HUD]{C_RESET} Projecting Neural Dashboard (v2.0 Neon)...")
    subprocess.Popen([sys.executable, "FXION_HUD_LAUNCHER.py"], 
                     creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)

def launch_master():
    print(f"{C_GOLD}[MASTER]{C_RESET} Injecting HYPERACTIVE OMEGA Engine into System Bios...")
    try:
        subprocess.run([sys.executable, "FXION_MASTER_CONTROL.py"], check=True)
    except KeyboardInterrupt:
        print(f"\n{C_MAGENTA}[BIOS]{C_RESET} Manual Override: Stealth Shutdown.")
    except Exception as e:
        print(f"\n{C_RED}[CRITICAL_HALT]{C_RESET} Neural Collapse: {e}")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{C_CYAN}" + "=" * 72 + f"{C_RESET}")
    print(f"{C_CYAN}|{C_RESET}   {C_BOLD}{C_MAGENTA}FXION-ONYX{C_RESET} // {C_BOLD}{C_CYAN}DYSON NEURAL AI BIOS{C_RESET} // {C_BOLD}{C_GOLD}DELTA-9.3.7{C_RESET}   {C_CYAN}|{C_RESET}")
    print(f"{C_CYAN}" + "=" * 72 + f"{C_RESET}")
    
    if check_dependencies():
        launch_hud()
        time.sleep(2)
        launch_master()
    else:
        input(f"\n{C_RED}>> SYSTEM HALTED. Press Enter to abort...{C_RESET}")

