
"""
FXION HUD LAUNCHER -- Local Web Server
Bypasses browser CORS restrictions to connect the HUD to real-time data.
"""
import http.server
import socketserver
import webbrowser
import os
import threading
import time

PORT = 8080
DIRECTORY = "dashboard"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n[HUD] Server started at http://localhost:{PORT}/fxion_hud.html")
        httpd.serve_forever()

if __name__ == "__main__":
    # Ensure live_stats.json exists or create a dummy one so the HUD doesn't error
    stats_path = os.path.join(DIRECTORY, "live_stats.json")
    if not os.path.exists(stats_path):
        with open(stats_path, "w") as f:
            f.write('{"status": "OFFLINE", "psi": 0, "hashrate": "0 KH/s", "total_mined": "0 BTC", "gpu": {"load":0, "temp":0}}')

    # Start server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    time.sleep(1)
    print("[HUD] Opening browser...")
    webbrowser.open(f"http://localhost:{PORT}/fxion_hud.html")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[HUD] Stopping server.")
