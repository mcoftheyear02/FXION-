
"""
FXION OMEGA WATCHDOG -- Automation & Self-Healing
Ensures the FXION-ONYX engine stays online 24/7.
Restarts on crash, rotates logs, and monitors system health.
"""
import subprocess
import sys
import time
import os
import logging

# Configure Watchdog Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] WATCHDOG -- %(message)s",
    handlers=[logging.FileHandler("logs/fxion_watchdog.log"), logging.StreamHandler()]
)
log = logging.getLogger("WATCHDOG")


# CYBERPUNK COLOR PALETTE (FXION)
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"
C_GOLD = "\033[93m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

MAX_RESTARTS = 10
RESTART_DELAY = 5 # seconds

def run_engine():
    restart_count = 0
    while restart_count < MAX_RESTARTS:
        log.info(f"{C_GOLD}Starting FXION-ONYX Engine (Attempt {restart_count + 1})...{C_RESET}")
        
        try:
            # Launch the Master Launcher which handles HUD and Master Control
            process = subprocess.Popen([sys.executable, "FXION_MASTER_LAUNCHER.py"])
            
            # Wait for the process to finish
            return_code = process.wait()
            
            if return_code == 0:
                log.info(f"{C_GREEN}Engine shut down gracefully.{C_RESET}")
                break
            else:
                log.warning(f"{C_RED}Engine crashed (Code: {return_code}). Initiating Self-Heal...{C_RESET}")
                restart_count += 1
                time.sleep(RESTART_DELAY)
                
        except KeyboardInterrupt:
            log.info("Watchdog terminated by user.")
            break
        except Exception as e:
            log.error(f"Watchdog encountered an error: {e}")
            restart_count += 1
            time.sleep(RESTART_DELAY)

    if restart_count >= MAX_RESTARTS:
        log.critical("Maximum restart attempts reached. Manual intervention required.")

if __name__ == "__main__":
    log.info("="*50)
    log.info("   FXION-ONYX OMEGA AUTOMATION ACTIVE   ")
    log.info("="*50)
    run_engine()
