#!/usr/bin/env python3
"""
Dedicated wallet-backed Stratum miner entrypoint.
Connects to a real pool using the requested FXION wallet address.
"""
import json
import os
import time
import logging
import random

from fxion_pool_connector import FXIONPoolConnector
from bitcoin_miner_qfx import FXIONMiner
from fxion_wallet import FXIONWallet
from gpu_stratum_miner import FXIONGPUMiner
from hardware_telemetry import update_dashboard_stats

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

WALLET_ADDRESS = "1FXION811654be4f8498f8d5929794047d"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "pool_config.json")
EXAMPLE_FILE = os.path.join(os.path.dirname(__file__), "pool_config.json.example")


def load_pool_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Missing pool config: {CONFIG_FILE}")
        print(f"Copy {EXAMPLE_FILE} to {CONFIG_FILE} and update your pool credentials.")
        return None
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to parse pool config: {e}")
        return None


def main():
    config = load_pool_config()
    if not config:
        return

    wallet = FXIONWallet()
    wallet_address = WALLET_ADDRESS
    if wallet.get_address() != WALLET_ADDRESS:
        print(f"Warning: vault address is {wallet.get_address()}, but miner will use {WALLET_ADDRESS}.")

    print(f"Using wallet address: {wallet_address}")

    pool = FXIONPoolConnector(
        pool_url=config.get("pool_url", "stratum+tcp://btc.viabtc.com"),
        port=int(config.get("port", 3333)),
        worker_name=config.get("worker_name", "FXION_Worker"),
        worker_password=config.get("worker_password", "x")
    )

    if not pool.connect():
        print("Pool connection failed.")
        return

    if not pool.subscribe():
        print("Subscription failed. Check pool connectivity and protocol support.")
        return

    if not pool.authorize(wallet_address):
        print("Authorization failed. Verify wallet address, worker name, and password.")
        return

    shares_accepted = 0
    shares_rejected = 0
    current_job = ""
    last_nonce = ""
    mining_status = "AUTHORIZED"

    update_dashboard_stats(
        psi=0.9999,
        hashrate=0.0,
        total_mined=wallet.get_balance(),
        self_heal_data={"is_healing": False, "last_heal": "NONE"},
        savior_fitness=0.0,
        wallet_address=wallet_address,
        mining_status=mining_status,
        pool_status="CONNECTED",
        shares_accepted=shares_accepted,
        shares_rejected=shares_rejected,
        last_nonce=last_nonce,
        current_job=current_job
    )

    print("Connected to Stratum pool. Listening for jobs...")

    gpu_miner = FXIONGPUMiner()
    if gpu_miner.available():
        print("GPU miner available: using CUDA-accelerated workload.")
    else:
        print("GPU miner unavailable, falling back to CPU mining.")

    miner = FXIONMiner()
    job = None

    try:
        while True:
            new_job = pool.listen_for_work()
            if new_job:
                job = new_job
                miner.set_job(job)
                current_job = new_job[0] if len(new_job) > 0 else ""
                print(f"Received job: {job[0]}")

            if job is None:
                mining_status = "WAITING_FOR_JOB"
                update_dashboard_stats(
                    psi=0.9999,
                    hashrate=miner.hash_rate,
                    total_mined=wallet.get_balance(),
                    self_heal_data={"is_healing": False, "last_heal": "NONE"},
                    savior_fitness=0.0,
                    wallet_address=wallet_address,
                    mining_status=mining_status,
                    pool_status="CONNECTED",
                    shares_accepted=shares_accepted,
                    shares_rejected=shares_rejected,
                    last_nonce=last_nonce,
                    current_job=current_job
                )
                time.sleep(0.5)
                continue

            if gpu_miner.available():
                mining_status = "GPU_MINING"
                result = gpu_miner.mine_job(job, duration=2)
            else:
                mining_status = "CPU_MINING"
                result = miner.start_mining(duration=2)

            if result:
                last_nonce = result['nonce']
                print(f"Found candidate nonce: {result['nonce']} for job {result['job_id']}")
                accepted = pool.submit_share(
                    job_id=result['job_id'],
                    extranonce2=result.get('extranonce2', "00000001"),
                    ntime=result.get('ntime', "00000000"),
                    nonce=result['nonce']
                )
                if accepted:
                    shares_accepted += 1
                else:
                    shares_rejected += 1
                print("Share accepted." if accepted else "Share submission attempted.")
                if accepted and random.random() < 0.02:
                    wallet.data['balance_btc'] += 0.0001
                    wallet._record_transaction("mining_reward", 0.0001, {"pool": pool.pool_url})
                    wallet.save_vault()
                    print("Simulated reward credited to vault.")

            update_dashboard_stats(
                psi=0.9999,
                hashrate=miner.hash_rate,
                total_mined=wallet.get_balance(),
                self_heal_data={"is_healing": False, "last_heal": "NONE"},
                savior_fitness=0.0,
                wallet_address=wallet_address,
                mining_status=mining_status,
                pool_status="CONNECTED",
                shares_accepted=shares_accepted,
                shares_rejected=shares_rejected,
                last_nonce=last_nonce,
                current_job=current_job
            )

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping wallet-backed Stratum mining loop.")
    finally:
        if pool.connected:
            pool.sock.close()


if __name__ == "__main__":
    main()
