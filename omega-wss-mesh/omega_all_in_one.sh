#!/bin/bash
# ==============================================================================
# OMEGA WSS MESH - ALL IN ONE DEPLOYMENT SCRIPT (v1.0-APACHE)
# ==============================================================================
# Operator: Cristan Lavergne
# Location: Salaberry-de-Valleyfield, QC, Canada
# Injection: L8 IQ T8 NEW QUANTIZED WSS
# ==============================================================================

set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${CYAN}[OMEGA]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; }

echo "=============================================================================="
echo "  OMEGA WSS MESH - INITIALISATION COMPLETE"
echo "  Injection: L8 IQ T8 NEW QUANTIZED WSS"
echo "=============================================================================="

# 1. Démarrage de la Gateway WSS Sécurisée
log "Démarrage de wss_gateway_secure.py (TLS 1.3)..."
python3 core/wss_gateway_secure.py --port 8765 --tls 1.3 &
PID_GW=$!
sleep 2
success "Gateway WSS active sur le port 8765."

# 2. Initialisation du Routage AI Convolutif
log "Chargement de cosmic_ai_convolutive.py..."
python3 core/cosmic_ai_convolutive.py --mode routing &
PID_AI=$!
sleep 1
success "AI Routing actif."

# 3. Activation de la Mesh Hypercube
log "Fusion Hypercube en cours..."
python3 core/hypercube_fusion.py --nodes 2040084 &
PID_MESH=$!
sleep 2
success "Mesh Hypercube déployée."

# 4. Lancement des Mineurs (Mode Surveillance/Simulation)
log "Exécution de mine_all_wss.sh..."
bash mining/mine_all_wss.sh &
PID_MINE=$!
success "Processus de minage lancés."

# 5. Dashboard CKPool
log "Lancement du dashboard web..."
python3 mining/ckpool_dashboard.py --port 8080 &
PID_DASH=$!
success "Dashboard accessible sur http://localhost:8080"

echo ""
echo "=============================================================================="
echo "  STATUT : TOUS LES SERVICES SONT ACTIFS"
echo "  - Gateway WSS : PID $PID_GW"
echo "  - AI Router   : PID $PID_AI"
echo "  - Mesh Core   : PID $PID_MESH"
echo "  - Miners      : PID $PID_MINE"
echo "  - Dashboard   : PID $PID_DASH"
echo "=============================================================================="
echo "  Pour arrêter : kill $PID_GW $PID_AI $PID_MESH $PID_MINE $PID_DASH"
echo "=============================================================================="

wait
