OMEGA WSS MESH - v1.0-APACHE
=============================

Injection: L8 IQ T8 NEW QUANTIZED WSS
Opérateur: Cristan Lavergne
Localisation: Salaberry-de-Valleyfield, QC, Canada

COMPOSANTS:
-----------
core/
  - wss_gateway_secure.py       : Gateway WebSocket TLS 1.3
  - cosmic_ai_convolutive.py    : Routage IA par réseaux convolutifs
  - hypercube_fusion.py         : Gestionnaire de Mesh Hypercube (2M+ nœuds)

mining/
  - mine_all_wss.sh             : Lanceur de tous les mineurs
  - ckpool_monitor_sim.py       : Surveillance CKPool Mainnet (Sécurisé/Simulé)
  - testnet_worker.py           : Worker Testnet4 (Minage réel sans risque)
  - cpu_randomx_worker.py       : Worker Monero (Compatible CPU)
  - ckpool_dashboard.py         : Dashboard Web HTML temps réel

SCRIPTS PRINCIPAUX:
-------------------
- omega_all_in_one.sh    : Déploiement complet du système
- update_wss_all.sh      : Mise à jour des modules WSS

INSTALLATION:
-------------
1. Installer les dépendances:
   pip install websockets numpy

2. Lancer le système:
   chmod +x omega_all_in_one.sh
   ./omega_all_in_one.sh

3. Accéder au dashboard:
   http://localhost:8080

CONFIGURATION:
--------------
Modifier omega_config_d00.json à la racine pour ajuster:
- Vecteur de cohérence (défaut: 1.0+0.0i)
- Entropie (défaut: Binaire [0,1])
- Nœuds de la flotte et de Dyson

LICENSE: APACHE 2.0
===================
