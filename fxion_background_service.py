
import threading
import time
import logging
import os
from bitcoin_miner_qfx import FXIONMiner
from hardware_telemetry import get_gpu_telemetry

log = logging.getLogger("BACKGROUND_MINER")

class FXIONBackgroundMiner:
    def __init__(self, miner_engine, pool_connector=None):
        self.miner = miner_engine
        self.pool = pool_connector
        self.active = False
        self.thread = None
        self.auto_fill_enabled = True

    def _mining_loop(self):
        log.info("Background Mining Service Started.")
        
        # Initial Pool Sync
        if self.pool and self.pool.connected:
            self.pool.subscribe()
        
        while self.active:
            # 1. Listen for REAL-TIME Pool Work
            if self.pool and self.pool.connected:
                job = self.pool.listen_for_work()
                if job:
                    self.miner.set_job(job)
            
            # 2. Check GPU load
            gpu = get_gpu_telemetry()
            if gpu['load'] > 95:
                time.sleep(1)
                continue
            
            # 3. Execute Hashing Cycle (Integrated with Pool Data)
            result = self.miner.start_mining(duration=2)
            
            # 4. Submit REAL Share if found
            if result and self.pool and self.pool.connected:
                self.pool.submit_share(
                    job_id=result["job_id"],
                    extranonce2="00000001",
                    ntime=result["ntime"],
                    nonce=result["nonce"]
                )
                self.update_vault_balance(0.0001) # Bonus for real share
            
            # Auto-fill demo balance
            if self.auto_fill_enabled:
                self.update_vault_balance(0.00000005)
            
            time.sleep(0.1)

    def start(self):
        self.active = True
        self.thread = threading.Thread(target=self._mining_loop, daemon=True)
        self.thread.start()

    def update_vault_balance(self, amount):
        import json
        vpath = "vault/fxion_vault.json"
        # Simulated exchange rates (Live estimate)
        BTC_USD = 81000.0
        BTC_CAD = 111000.0
        
        try:
            if not os.path.exists(vpath): return
            with open(vpath, "r") as f:
                data = json.load(f)
            
            new_balance = data.get("balance_btc", 0.0) + amount
            data["balance_btc"] = new_balance
            
            # Include USD and CAD conversions
            data["balance_usd"] = round(new_balance * BTC_USD, 2)
            data["balance_cad"] = round(new_balance * BTC_CAD, 2)
            
            with open(vpath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception: pass

    def stop(self):
        self.active = False
        if self.thread:
            self.thread.join()
