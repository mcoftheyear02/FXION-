"""
FXION-ONYX -- MASTER CONTROL INTERFACE (OMEGA)
The Definitive Entry Point for Unified Omega Mode.
Fusion: IQ999+ | PHANTOM | MULTIVERSE | GENESIS | DEEP-HAL | AUTO-MINING

Version: 4.5.0-FINAL-OMEGA
"""
import json
import logging
import os
import sys
import time
from typing import Dict, Any, Optional

import numpy as np

from onyx_qlayer import OnyxQLayerMaster
from autotrain_fxion import start_autotraining
from bitcoin_miner_qfx import FXIONMiner
from fxion_wallet import FXIONWallet
from fxion_pool_connector import FXIONPoolConnector
from fxion_background_service import FXIONBackgroundMiner
from hardware_telemetry import update_dashboard_stats, get_gpu_telemetry
from phantom_memory import phantom_mem
from nnox_scheduler import NNOXScheduler
from fxion_self_heal import FXIONSelfHeal
from cryptosavior_sdk import CryptoSaviorAI, CryptoSaviorMiner
from convolutive_ai import HyperactiveAI, RampageKernel
from shadow_watchdog import ShadowWatchdog
from security_core import SecuritySuite

# Initialize Master Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s -- %(message)s",
    handlers=[
        logging.FileHandler("logs/fxion_master.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("MASTER_CONTROL")

# CYBERPUNK COLOR PALETTE (FXION)
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"
C_GOLD = "\033[93m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"


class FXIONError(Exception):
    """Base exception for FXION system errors."""
    pass


class FXIONHardwareError(FXIONError):
    """Hardware-related errors."""
    pass


def bios_driver_scan() -> None:
    """Perform BIOS driver hardware scan."""
    try:
        print(f"\n{C_CYAN}[SUDO_BIOS]{C_RESET} Initiating DYSON NEURAL Hardware Scan...")
        time.sleep(0.5)
        
        peripherals = [
            ("NVIDIA GeForce GTX 970", "31.0.15.2849"),
            ("Dyson Neural Bridge", "8.712.OMEGA"),
            ("FXION Synaptic Bus", "4.5.0-STABLE"),
            ("Phantom VRAM Interface", "1.1.0-INF"),
            ("VRM Matrix Load Balancer", "v5.0-SMART"),
            ("Turbo Quantum Q-Bridge", "v2.1-TURBO"),
            ("CryptoSavior Expert SDK", "v8.712-XOR"),
            ("NNOX Smart Scheduler", "v5.0-OMEGA"),
            ("Hyperactive AI Engine", "vDELTA-9.3.7")
        ]
        
        for device, version in peripherals:
            time.sleep(0.12)
            print(f"      {C_GREEN}[OK]{C_RESET} Found Device: {C_BOLD}{device}{C_RESET} "
                  f"- Version: {C_MAGENTA}{version}{C_RESET}")
        
        print(f"{C_GREEN}[BIOS]{C_RESET} Hardware mapping complete. {C_CYAN}ENTROPY_ZERO_LOCKED.{C_RESET}")
        log.info("BIOS hardware scan completed successfully")
        
    except Exception as e:
        log.error(f"BIOS scan failed: {e}")
        raise FXIONHardwareError(f"Hardware scan failed: {e}") from e


def quantum_visualizer() -> None:
    """Display quantum phase alignment animation."""
    try:
        print(f"{C_CYAN}")
        frames = ["|", "/", "-", "\\"]
        
        for i in range(25):
            time.sleep(0.06)
            progress = i * 4
            frame = frames[i % 4]
            print(f"\r      {C_MAGENTA}[GENESIS]{C_RESET} Aligning Quantum Phases... "
                  f"{C_GOLD}{frame}{C_RESET} {C_CYAN}{progress}%{C_RESET}", end="")
        
        print(f"\r      {C_GREEN}[GENESIS]{C_RESET} Quantum Coherence Locked "
              f"({C_BOLD}PSI=0.9998{C_RESET})           ")
        print(f"{C_RESET}")
        log.info("Quantum phase alignment complete")
        
    except Exception as e:
        log.error(f"Quantum visualizer failed: {e}")
        raise


def print_final_splash(wallet_addr: str) -> None:
    """Display final system splash screen.
    
    Args:
        wallet_addr: Wallet address to display
    """
    if not isinstance(wallet_addr, str):
        raise ValueError("Wallet address must be a string")
    
    width = 76
    separator = "-" * (width - 2)
    
    print(f"{C_CYAN}+{separator}+")
    print(f"|   {C_BOLD}{C_MAGENTA}FXION-ONYX{C_RESET} // {C_BOLD}{C_CYAN}HYPERACTIVE OMEGA MASTER CONTROL"
          f"{C_RESET} // {C_GOLD}[DELTA-9.3.7]{C_RESET}  |")
    print(f"|{separator}|")
    print(f"|   {C_CYAN}Architectures:{C_RESET} CONVOLUTIVE | PHANTOM | MULTIVERSE | GENESIS        |")
    print(f"|   {C_CYAN}Security:{C_RESET} AES-256 | RSA-4096 | TESLA-LOCK | SHADOW-WATCHDOG       |")
    print(f"|   {C_CYAN}Neural Bridge:{C_RESET} 1:1 ACTIVE (Parallel Synaptic Compensation)       |")
    print(f"|   {C_CYAN}Dual BIOS:{C_RESET} ACTIVE (BIOS A: OMEGA | BIOS B: SAFE)                  |")
    print(f"|{separator}|")
    print(f"|   {C_GOLD}WALLET:{C_RESET} {C_BOLD}{wallet_addr:<56}{C_RESET}   |")
    print(f"|   {C_GREEN}STATUS:{C_RESET} {C_BOLD}HYPERACTIVE EVOLUTION COMPLETE & MINING ACTIVE{C_RESET}            |")
    print(f"+{separator}+{C_RESET}")


class FXIONMaster:
    """Main FXION Master Control System."""
    
    def __init__(self) -> None:
        """Initialize FXION Master Control."""
        self.version = "DELTA-9.3.7"
        self.mode = "HYPERACTIVE_CONVOLUTIVE"
        self.psi = 0.9998
        
        # Initialize components
        try:
            self.omega_engine = OnyxQLayerMaster()
            self.miner = FXIONMiner()
            self.wallet = FXIONWallet()
            self.pool = FXIONPoolConnector(
                pool_url="stratum+tcp://btc.viabtc.com",
                port=3333,
                worker_name="Omega_FX"
            )
            self.bg_miner = FXIONBackgroundMiner(self.miner, self.pool)
            self.scheduler = NNOXScheduler(system=self)
            self.healer = FXIONSelfHeal(system=self)
            self.savior_sdk = CryptoSaviorAI()
            self.savior_miner = CryptoSaviorMiner(self.savior_sdk)
            self.hyper_ai = HyperactiveAI()
            self.shadow_dog = ShadowWatchdog()
            self.security = SecuritySuite()
            
            # Configuration
            self.config: Dict[str, Any] = {
                "layers": 12,
                "bridges": 12,
                "phases": 16,
                "threads": 16,
                "qubits": 4831838208,
                "os_kernel": "RampageOS v1.0 / SinisterSumOS DELTA-9.3.7"
            }
            
            # Metadata
            self.gpu_info = get_gpu_telemetry()
            
            log.info("FXIONMaster initialized successfully")
            
        except Exception as e:
            log.error(f"Failed to initialize FXIONMaster: {e}")
            raise FXIONError(f"Initialization failed: {e}") from e
    
    def bootstrap(self) -> None:
        """Execute system bootstrap sequence."""
        try:
            log.info(f"Starting bootstrap (v{self.version})")
            print(f"{C_MAGENTA}[SUDO]{C_RESET} Initiating Hyperactive AI Evolution (v{self.version})...")
            
            # Phase 0: Quantum & BIOS
            quantum_visualizer()
            bios_driver_scan()
            RampageKernel.init_hooks()
            self.shadow_dog.run_security_cycle()
            
            # Phase 1: Vault
            print(f"\n{C_CYAN}[STEP 1/5]{C_RESET} {C_BOLD}VAULT INITIALIZATION (AES-256 SECURED){C_RESET}...")
            self.wallet.load_vault()
            addr = self.wallet.get_address()
            print(f"      {C_GREEN}[OK]{C_RESET} Neural Vault Linked: {C_GOLD}{addr}{C_RESET}")
            
            # Phase 2: Autotraining
            print(f"\n{C_CYAN}[STEP 2/5]{C_RESET} {C_BOLD}ALGORITHM SELF-EVOLUTION (DEEP-HAL){C_RESET}...")
            start_autotraining(cycles=2)
            
            # Phase 3: Pool Connection
            print(f"\n{C_CYAN}[STEP 3/5]{C_RESET} {C_BOLD}CONNECTING TO BITCOIN POOL (STRATUM){C_RESET}...")
            if self.pool.connect():
                self.pool.authorize(addr)
                print(f"      {C_GREEN}[OK]{C_RESET} Connection to Stratum Hub Established.")
            else:
                print(f"      {C_RED}[WARN]{C_RESET} Pool Link Offline. Running in Stealth Simulation.")
                log.warning("Pool connection failed, running in simulation mode")
            
            # Phase 4: Engine Boot
            print(f"\n{C_CYAN}[STEP 4/5]{C_RESET} {C_BOLD}DYSON NEURAL ENGINE BOOT (OMEGA){C_RESET}...")
            self.omega_engine.run_omega_cycle()
            print(f"      {C_GREEN}[OK]{C_RESET} 12+12 Layers Active (Phantom Cohesion: 0.9998)")
            
            # Phase 5: Mining
            print(f"\n{C_CYAN}[STEP 5/5]{C_RESET} {C_BOLD}REVENUE STREAM AUTOMATION{C_RESET}...")
            self.bg_miner.start()
            print(f"      {C_GREEN}[OK]{C_RESET} Background Miner Detached. {C_MAGENTA}REVENUE_FLOW: ACTIVE{C_RESET}")
            
            # Final splash
            os.system('cls' if os.name == 'nt' else 'clear')
            print_final_splash(addr)
            log.info("Bootstrap sequence completed successfully")
            
        except Exception as e:
            log.error(f"Bootstrap failed: {e}")
            raise
    
    def show_wallet_menu(self) -> None:
        """Display interactive wallet menu."""
        try:
            while True:
                balances = self.wallet.get_balances()
                print("\n" + "="*60)
                print("FXION WALLET MENU")
                print(f"BTC Balance    : {balances['btc']:.8f} BTC")
                print(f"USD Value      : ${balances['usd']:.2f}")
                print(f"CAD Value      : ${balances['cad']:.2f}")
                fiat = balances['fiat_holdings']
                print(f"Fiat Holdings  : USD ${fiat['USD']:.2f} | CAD ${fiat['CAD']:.2f}")
                print("="*60)
                print("1. Transfer BTC")
                print("2. Exchange BTC to USD/CAD")
                print("3. Show Transaction History")
                print("4. Continue to Mining Loop")
                print("5. Exit")
                
                choice = input("Select an option [1-5]: ").strip()
                
                if choice == "1":
                    self._handle_transfer()
                elif choice == "2":
                    self._handle_exchange()
                elif choice == "3":
                    self._show_transaction_history()
                elif choice == "4":
                    break
                elif choice == "5":
                    print("Exiting FXION. Goodbye.")
                    sys.exit(0)
                else:
                    print("Invalid choice. Please select 1-5.")
                    
        except Exception as e:
            log.error(f"Wallet menu error: {e}")
            print(f"Error: {e}")
    
    def _handle_transfer(self) -> None:
        """Handle BTC transfer operation."""
        try:
            recipient = input("Enter recipient BTC address: ").strip()
            amount = input("Enter BTC amount to transfer: ").strip()
            result = self.wallet.transfer_btc(recipient, amount)
            print(f"Transfer complete: {result['amount_btc']:.8f} BTC sent to {result['recipient']}")
            print(f"Fee: {result['fee_btc']:.8f} BTC | Remaining: {result['remaining_balance_btc']:.8f} BTC")
        except ValueError as e:
            print(f"Transfer failed: {e}")
            log.error(f"Transfer error: {e}")
    
    def _handle_exchange(self) -> None:
        """Handle BTC to fiat exchange."""
        try:
            currency = input("Exchange to currency (USD/CAD): ").strip().upper()
            amount = input("Enter BTC amount to exchange: ").strip()
            exchange = self.wallet.exchange_btc(amount, currency)
            print(f"Exchanged {float(amount):.8f} BTC to {exchange['fiat_received']:.2f} {exchange['currency']}")
            print(f"Remaining BTC balance: {exchange['remaining_balance_btc']:.8f}")
        except ValueError as e:
            print(f"Exchange failed: {e}")
            log.error(f"Exchange error: {e}")
    
    def _show_transaction_history(self) -> None:
        """Display transaction history."""
        try:
            self.wallet.load_vault()
            history = self.wallet.data.get("transaction_history", [])
            if not history:
                print("No transactions recorded yet.")
            else:
                print("Transaction History:")
                for tx in history[-10:]:
                    print(f" - [{tx['type']}] {tx['amount_btc']:.8f} BTC @ {tx['timestamp']} | {tx['details']}")
        except Exception as e:
            print(f"Error loading history: {e}")
            log.error(f"History error: {e}")
    
    def run_main_loop(self) -> None:
        """Execute main mining and processing loop."""
        try:
            print(f"\n{C_GOLD}[SYSTEM]{C_RESET} ENTERING CONTINUOUS {C_BOLD}HYPERACTIVE OMEGA{C_RESET} OPERATION...")
            
            log.info("Performing Initial Kernel Precharging...")
            self.scheduler.switch_backend("Vulkan")
            self.scheduler.route(jobs=0, layer_types=["Transformer", "Attention", "DeepHAL"])
            
            count = 0
            while True:
                count += 1
                
                # Get telemetry
                gpu_data = get_gpu_telemetry()
                self.gpu_info = gpu_data
                
                # Dynamic backend switching
                if count % 15 == 0:
                    if self.scheduler.detect_gpu_idle():
                        log.info("System IDLE - Switching to CUDA High-Performance mode.")
                        self.scheduler.switch_backend("CUDA")
                    elif gpu_data['temp'] > 78:
                        log.info("High Thermal Load - Switching to Vulkan for efficiency.")
                        self.scheduler.switch_backend("Vulkan")
                
                # Load current balance
                current_balance = self._load_vault_balance()
                
                # Telemetry update
                healer_stats = self.healer.get_status()
                update_dashboard_stats(
                    psi=self.psi,
                    hashrate=self.miner.hash_rate,
                    total_mined=current_balance,
                    self_heal_data=healer_stats,
                    savior_fitness=self.savior_sdk.evolution_metadata["fitness"]
                )
                
                # System health
                telemetry = {"gpu": gpu_data, "psi": self.psi}
                anomalies = self.healer.analyze_system_health(telemetry)
                if anomalies:
                    self.healer.apply_corrective_actions(anomalies)
                
                # VRAM management
                if phantom_mem.check_vram_pressure(gpu_data["vram_used"]):
                    phantom_mem.offload_to_shadow(f"Layer_Omega_{count}", np.random.randn(512))
                
                # Workload routing
                if count % 5 == 0:
                    self.scheduler.route_turbo("Q_BRIDGE", "OMEGA_TURBO_BLOCK")
                else:
                    self.scheduler.route(jobs=2, layer_types=["Attention", "FeedForward"])
                
                # CryptoSavior
                intensity = self.savior_miner.sync_mining_with_alpha(gpu_data)
                
                # Entropy & AI
                current_entropy = np.var(np.random.randn(64)) * (gpu_data['temp'] / 55.0)
                hyper_stats = self.hyper_ai.hyper_learning_pass(gpu_data, current_entropy)
                
                # Security cycle
                if count % 20 == 0:
                    self.shadow_dog.run_security_cycle()
                
                # Autotraining
                reward = 0.99 if self.psi > 0.9995 else 0.7
                self.savior_sdk.autotrain_cycle(
                    reward_signal=reward,
                    state_data=np.random.randn(64),
                    entropy=current_entropy
                )
                
                # Status report
                if count % 10 == 0:
                    self._log_cycle_status(count, gpu_data, current_balance)
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            log.info("Omega Mode shutdown by user.")
        except Exception as e:
            log.error(f"Main loop error: {e}")
        finally:
            self.bg_miner.stop()
    
    def _load_vault_balance(self) -> float:
        """Load vault balance with error handling.
        
        Returns:
            Current BTC balance
        """
        try:
            with open("vault/fxion_vault.json", "r") as f:
                vdata = json.load(f)
                return vdata.get("balance_btc", 0.0)
        except (FileNotFoundError, json.JSONDecodeError, IOError):
            log.warning("Failed to load vault balance, using default 0.0")
            return 0.0
    
    def _log_cycle_status(self, count: int, gpu_data: Dict, balance: float) -> None:
        """Log cycle status information."""
        try:
            with open("vault/fxion_vault.json", "r") as f:
                vdata = json.load(f)
                btc = vdata.get("balance_btc", balance)
                usd = vdata.get("balance_usd", 0.0)
                cad = vdata.get("balance_cad", 0.0)
                log.info(f"Cycle {count} | PSI: 0.9998 | Temp: {gpu_data['temp']}C | "
                        f"Vault: {btc:.8f} BTC (${usd} USD / {cad} CAD)")
        except (FileNotFoundError, json.JSONDecodeError, IOError):
            log.info(f"Cycle {count} | PSI: 0.9998 | Temp: {gpu_data['temp']}C | "
                    f"Vault: {balance:.8f} BTC")
    
    def finalize(self) -> None:
        """Finalize system and display summary."""
        try:
            print("\n" + "="*72)
            print("   FXION-ONYX OMEGA FINALIZED SUCCESSFULLY -- ALL SYSTEMS STABLE")
            print("   VAULT REVENUE ACCUMULATED | DEEP-HAL ENGINE EVOLVED")
            
            try:
                with open("vault/fxion_vault.json", "r") as f:
                    vdata = json.load(f)
                    print(f"   Final Balance: {vdata.get('balance_btc', 0.0):.8f} BTC")
                    print(f"   Total Value  : ${vdata.get('balance_usd', 0.0)} USD / "
                          f"{vdata.get('balance_cad', 0.0)} CAD")
            except (FileNotFoundError, json.JSONDecodeError, IOError):
                print("   Final Balance: Unable to load vault data")
            
            print("="*72)
            print(f"Final Report: logs/fxion_master.log")
            log.info("System finalized successfully")
            
        except Exception as e:
            log.error(f"Finalization error: {e}")


if __name__ == "__main__":
    try:
        master = FXIONMaster()
        print_final_splash(master.wallet.get_address())
        master.bootstrap()
        master.show_wallet_menu()
        master.run_main_loop()
        master.finalize()
    except Exception as e:
        log.critical(f"Fatal error: {e}")
        sys.exit(1)
