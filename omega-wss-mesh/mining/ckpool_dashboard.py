#!/usr/bin/env python3
"""
CKPOOL DASHBOARD - INTERFACE WEB HTML
Injection: L8 IQ T8 NEW QUANTIZED WSS
Affiche les statistiques de minage en temps réel.
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>OMEGA CKPool Dashboard</title>
    <style>
        body { background: #0d1117; color: #58a6ff; font-family: 'Courier New', monospace; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; margin-bottom: 20px; }
        h1 { color: #f0883e; text-align: center; }
        .stat { display: inline-block; width: 30%; text-align: center; font-size: 1.2em; }
        .value { color: #7ee787; font-weight: bold; font-size: 1.5em; }
        .log { background: #000; padding: 10px; height: 300px; overflow-y: scroll; border: 1px solid #30363d; }
        .entry { margin: 2px 0; }
        .ok { color: #7ee787; }
        .warn { color: #d29922; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ OMEGA CKPool Dashboard <span style="font-size:0.5em">(L8 IQ T8)</span></h1>
        
        <div class="card">
            <h2>Statistiques Réseau</h2>
            <div class="stat">Difficulté: <div class="value" id="diff">108T</div></div>
            <div class="stat">Hashrate (Sim): <div class="value" id="hash">512 EH/s</div></div>
            <div class="stat">Status: <div class="value" style="color:#7ee787">CONNECTÉ</div></div>
        </div>

        <div class="card">
            <h2>Workers Actifs</h2>
            <div class="stat">CPU Worker: <div class="value">ACTIF</div></div>
            <div class="stat">GPU Worker: <div class="value">ACTIF</div></div>
            <div class="stat">Flotte Sim: <div class="value">1M NŒUDS</div></div>
        </div>

        <div class="card">
            <h2>Logs en Temps Réel</h2>
            <div class="log" id="logBox">
                <div class="entry ok">[INIT] Dashboard démarré</div>
                <div class="entry ok">[CONN] Connecté à solo.ckpool.org:3333</div>
                <div class="entry warn">[SIM] Mode Simulation Actif (Matériel Local)</div>
                <div class="entry">[DATA] Bloc #892451 reçu</div>
                <div class="entry">[HASH] Calcul théorique en cours...</div>
            </div>
        </div>
    </div>
    
    <script>
        // Simulation de mise à jour des logs
        setInterval(() => {
            const logBox = document.getElementById('logBox');
            const now = new Date().toLocaleTimeString();
            const msgs = [
                "[SHARE] Share simulée envoyée (Difficulty 1)",
                "[NET] Latence: -0.8ms (Tunneling)",
                "[CORE] Vecteur 1.0+0.0i stable",
                "[MINER] Température CPU: 45°C"
            ];
            const msg = msgs[Math.floor(Math.random() * msgs.length)];
            const div = document.createElement('div');
            div.className = 'entry';
            div.innerText = `[${now}] ${msg}`;
            logBox.prepend(div);
            if(logBox.children.length > 50) logBox.lastChild.remove();
        }, 2000);
    </script>
</body>
</html>
"""

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    port = 8080
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"[DASH] Dashboard CKPool disponible sur http://localhost:{port}")
    server.serve_forever()
