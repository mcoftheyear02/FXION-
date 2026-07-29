#!/bin/bash
# MINE ALL WSS - LANCEUR DE MINEURS
# Injection: L8 IQ T8 NEW QUANTIZED WSS

echo "[MINER] Initialisation des workers WSS..."

# Worker 1: Surveillance CKPool Mainnet (Simulation)
echo "[MINER] Lancement du monitor CKPool..."
python3 mining/ckpool_monitor_sim.py &
PID1=$!

# Worker 2: Testnet Miner (Si configuré)
echo "[MINER] Lancement du miner Testnet..."
python3 mining/testnet_worker.py &
PID2=$!

# Worker 3: Altcoin CPU Miner (Monero Ready)
echo "[MINER] Lancement du worker CPU RandomX..."
python3 mining/cpu_randomx_worker.py &
PID3=$!

echo "[OK] Tous les mineurs sont lancés."
echo "PIDs: $PID1, $PID2, $PID3"

wait
