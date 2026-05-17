
"""
FXION POOL CONNECTOR -- Stratum Protocol Interface
Connects the OMEGA Engine to global Bitcoin Mining Pools.
"""
import socket
import json
import logging
import time

log = logging.getLogger("POOL_CONNECTOR")

class FXIONPoolConnector:
    def __init__(self, pool_url="stratum+tcp://btc.viabtc.com", port=3333, worker_name="FXION_Worker", worker_password="x"):
        self.pool_url = pool_url.replace("stratum+tcp://", "")
        self.port = port
        self.worker_name = worker_name
        self.worker_password = worker_password
        self.mining_user = None
        self.sock = None
        self.connected = False
        self.extranonce1 = None
        self.extranonce2_size = None

    def connect(self):
        try:
            log.info(f"Connecting to Pool: {self.pool_url}:{self.port}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((self.pool_url, self.port))
            self.connected = True
            log.info("Successfully connected to Stratum Pool!")
            return True
        except Exception as e:
            log.error(f"Connection failed: {e}")
            return False

    def authorize(self, wallet_address):
        """Authenticates the FXION worker on the pool."""
        if not self.connected:
            return False
        try:
            auth_msg = {
                "params": [f"{wallet_address}.{self.worker_name}", self.worker_password],
                "id": 2,
                "method": "mining.authorize"
            }
            self.sock.sendall((json.dumps(auth_msg) + "\n").encode())
            responses = self._recv_json_messages(timeout=5)
            for msg in responses:
                if msg.get("id") == 2:
                    if msg.get("result") is True:
                        self.mining_user = auth_msg["params"][0]
                        log.info(f"Authorization accepted by pool for {self.mining_user}.")
                        return True
                    log.error(f"Authorization rejected: {msg.get('error')}")
                    return False
            log.error("Authorization failed: no response from pool.")
            return False
        except Exception as e:
            log.error(f"Authorization failed: {e}")
            return False

    def _recv_json_messages(self, timeout=5):
        messages = []
        if not self.connected:
            return messages

        self.sock.settimeout(timeout)
        try:
            raw = self.sock.recv(4096).decode(errors='ignore')
            for line in raw.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue
        except socket.timeout:
            pass
        except Exception as e:
            log.error(f"Pool read error: {e}")
        finally:
            self.sock.settimeout(None)
        return messages

    def subscribe(self):
        """Subscribes to the pool and gets extranonce."""
        if not self.connected:
            return False
        try:
            subscribe_msg = {
                "id": 1,
                "method": "mining.subscribe",
                "params": []
            }
            self.sock.sendall((json.dumps(subscribe_msg) + "\n").encode())
            responses = self._recv_json_messages(timeout=5)
            for res_json in responses:
                if res_json.get("result"):
                    self.extranonce1 = res_json["result"][1]
                    self.extranonce2_size = res_json["result"][2]
                    log.info(f"Subscribed. Extranonce1: {self.extranonce1}")
                    return True
            log.error("Subscription failed: no valid subscribe response")
        except Exception as e:
            log.error(f"Subscription failed: {e}")
        return False

    def listen_for_work(self):
        """Continuously listens for mining.notify from the pool."""
        if not self.connected:
            return None
        try:
            self.sock.setblocking(False)
            messages = self._recv_json_messages(timeout=0.5)
            for msg in messages:
                if msg.get("method") == "mining.notify":
                    log.info(f"NEW JOB RECEIVED: {msg['params'][0]}")
                    return msg["params"]
        except Exception as e:
            log.error(f"Pool read error: {e}")
        return None

    def submit_share(self, job_id, extranonce2, ntime, nonce):
        """Submits a found share to the pool."""
        if not self.connected:
            return False
        try:
            username = self.mining_user or self.worker_name
            submit_msg = {
                "params": [username, job_id, extranonce2, ntime, nonce],
                "id": 4,
                "method": "mining.submit"
            }
            self.sock.sendall((json.dumps(submit_msg) + "\n").encode())
            responses = self._recv_json_messages(timeout=5)
            for msg in responses:
                if msg.get("id") == 4:
                    if msg.get("result") is True:
                        log.info(f"Share accepted: Job {job_id} | Nonce {nonce}")
                        return True
                    log.error(f"Share rejected: {msg.get('error')}")
                    return False
            log.info(f"Share submitted: Job {job_id} | Nonce {nonce}")
            return True
        except Exception as e:
            log.error(f"Share submission failed: {e}")
            return False

if __name__ == "__main__":
    conn = FXIONPoolConnector()
    conn.connect()
