"""
NX SECURE SERVER IMPLEMENTATION
-------------------------------
Dedicated endpoint for IQ4_NL NET Layer connections.
Handles encrypted tunnels from remote clients.
"""

import socket
import ssl
import threading
import json
from datetime import datetime

class NXSecureServer:
    def __init__(self, host='0.0.0.0', port=9999, certfile='cert.pem', keyfile='key.pem'):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.server_socket = None
        self.clients = []
        self.running = False

    def generate_self_signed_cert(self):
        """Generate self-signed certs if not exist (for demo)."""
        import subprocess
        try:
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:4096",
                "-keyout", self.keyfile, "-out", self.certfile,
                "-days", "365", "-nodes", "-subj", "/CN=nx.secure.local"
            ], check=True)
            print(f"[NX] Certificates generated: {self.certfile}, {self.keyfile}")
        except Exception as e:
            print(f"[NX] Cert generation failed (install openssl): {e}")

    def start(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        except FileNotFoundError:
            print("[NX] Certs not found. Generating self-signed...")
            self.generate_self_signed_cert()
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"[NX] SECURE SERVER LISTENING on {self.host}:{self.port}")
        print("[NX] Waiting for IQ4_NL NET layer connections...")

        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                secure_sock = context.wrap_socket(client_sock, server_side=True)
                print(f"[NX] Client connected: {addr}")
                
                client_thread = threading.Thread(target=self.handle_client, args=(secure_sock, addr))
                client_thread.daemon = True
                client_thread.start()
                self.clients.append(secure_sock)
            except Exception as e:
                if self.running:
                    print(f"[NX] Accept error: {e}")

    def handle_client(self, sock, addr):
        try:
            while self.running:
                data = sock.recv(4096)
                if not data:
                    break
                
                packet = json.loads(data.decode('utf-8'))
                print(f"[NX][NET] Received from {addr}: {packet.get('protocol')} - {packet.get('layer')}")
                
                # Echo acknowledgment
                ack = {
                    "status": "ACK",
                    "timestamp": datetime.now().isoformat(),
                    "server": "NX_SECURE_V1",
                    "received": packet
                }
                sock.sendall(json.dumps(ack).encode('utf-8'))
        except Exception as e:
            print(f"[NX] Client error: {e}")
        finally:
            sock.close()
            if sock in self.clients:
                self.clients.remove(sock)
            print(f"[NX] Client disconnected: {addr}")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        print("[NX] Server stopped.")

if __name__ == "__main__":
    server = NXSecureServer(port=9999)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
