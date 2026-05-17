"""
IQ4_NL PROTOCOL SPLIT ARCHITECTURE
----------------------------------
Layer 1: NET (External) -> NX Secure Server Tunnel
Layer 2: LAN (Internal) -> Direct IQ Logic Injection
"""

import socket
import ssl
import json
import time
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class LinkType(Enum):
    NET = "NET"      # External Secure Tunnel
    LAN = "LAN"      # Internal Logic Bus
    IQ_DIRECT = "IQ_DIRECT" # Direct Config Injection

@dataclass
class Packet:
    header: str
    link_type: LinkType
    payload: Dict[str, Any]
    timestamp: float = time.time()
    signature: str = "IQ4_NL_SIGNED"

class NXSecureClient:
    """
    NET LAYER: Handles encrypted connection to NX Secure Server.
    Isolated from local logic processing.
    """
    def __init__(self, host: str, port: int, cert_file: Optional[str] = None):
        self.host = host
        self.port = port
        self.cert_file = cert_file
        self.socket = None
        self.connected = False
        
    def connect(self):
        """Establish TLS 1.3+ connection to NX Server."""
        try:
            context = ssl.create_default_context()
            if self.cert_file:
                context.load_verify_locations(self.cert_file)
            
            self.socket = socket.create_connection((self.host, self.port))
            secure_sock = context.wrap_socket(self.socket, server_hostname=self.host)
            self.connected = True
            print(f"[NET] Connected to NX Secure Server @ {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[NET] Connection Failed: {e}")
            self.connected = False
            return False

    def send_secure(self, data: Dict):
        """Transmit data over the secure NET channel."""
        if not self.connected:
            return False
        try:
            packet = json.dumps({
                "protocol": "IQ4_NL",
                "layer": "NET",
                "data": data
            }).encode('utf-8')
            self.socket.sendall(packet)
            return True
        except Exception as e:
            print(f"[NET] Transmission Error: {e}")
            return False

    def close(self):
        if self.socket:
            self.socket.close()
        self.connected = False

class LANLogicBus:
    """
    LAN LAYER: Local distribution of IQ signals.
    Directs IQ logic to the specific Config Engine.
    """
    def __init__(self):
        self.subscribers: Dict[str, Callable] = {}
        self.config_logic_active = False
        
    def register_logic(self, logic_id: str, callback: Callable):
        """Register a local config logic handler."""
        self.subscribers[logic_id] = callback
        print(f"[LAN] Logic '{logic_id}' registered for direct injection.")
        
    def inject_iq_direct(self, target_logic: str, iq_data: Dict):
        """
        Directly inject IQ parameters into the specified config logic.
        Bypasses external network stack.
        """
        if target_logic in self.subscribers:
            print(f"[LAN][IQ_DIRECT] Injecting into {target_logic}...")
            try:
                self.subscribers[target_logic](iq_data)
                return True
            except Exception as e:
                print(f"[LAN] Injection Error: {e}")
                return False
        else:
            print(f"[LAN] Target logic '{target_logic}' not found.")
            return False

class IQ4NLController:
    """
    Main Controller: Orchestrates the split between NET and LAN.
    """
    def __init__(self, nx_host: str, nx_port: int):
        self.net_layer = NXSecureClient(nx_host, nx_port)
        self.lan_layer = LANLogicBus()
        self.running = False
        
    def start_net_tunnel(self):
        """Initiate the NET layer connection."""
        return self.net_layer.connect()
        
    def route_packet(self, packet: Packet):
        """
        Router: Decides whether to send via NET or process via LAN.
        """
        if packet.link_type == LinkType.NET:
            # Forward to NX Secure Server
            self.net_layer.send_secure(packet.payload)
        elif packet.link_type == LinkType.LAN:
            # Process locally
            target = packet.payload.get("target_logic", "default_config")
            self.lan_layer.inject_iq_direct(target, packet.payload)
        elif packet.link_type == LinkType.IQ_DIRECT:
            # High priority direct config update
            target = packet.payload.get("target_logic", "default_config")
            self.lan_layer.inject_iq_direct(target, packet.payload)
            
    def create_net_packet(self, data: Dict) -> Packet:
        return Packet(header="NX_SECURE", link_type=LinkType.NET, payload=data)
    
    def create_lan_packet(self, target: str, data: Dict) -> Packet:
        data["target_logic"] = target
        return Packet(header="LOCAL_IQ", link_type=LinkType.LAN, payload=data)

# Example Usage / Demo
if __name__ == "__main__":
    # Initialize Controller (Pointing to dummy NX server for demo)
    controller = IQ4NLController("nx.secure.local", 9999)
    
    # Define a mock Config Logic
    def my_config_logic_engine(data):
        print(f">>> CONFIG LOGIC EXECUTED: {data}")
        
    # Register Logic on LAN Layer
    controller.lan_layer.register_logic("my_config_logic_engine", my_config_logic_engine)
    
    # Simulate Split Traffic
    print("\n--- TESTING IQ4_NL SPLIT ARCHITECTURE ---")
    
    # 1. NET Traffic (To NX Server)
    net_pkt = controller.create_net_packet({"status": "sync", "source": "galaxy_map"})
    print(f"Sending NET packet: {net_pkt.header}")
    # controller.start_net_tunnel() # Uncomment if NX server is real
    
    # 2. LAN Traffic (Direct to Config Logic)
    lan_pkt = controller.create_lan_packet(
        target="my_config_logic_engine", 
        data={"elliptical_angle": 60.5, "seismo_gain": 1.2}
    )
    controller.route_packet(lan_pkt)
    
    # 3. IQ_DIRECT Traffic
    iq_pkt = Packet(
        header="OVERRIDE",
        link_type=LinkType.IQ_DIRECT,
        payload={"target_logic": "my_config_logic_engine", "quantum_state": "ENTANGLED"}
    )
    controller.route_packet(iq_pkt)
