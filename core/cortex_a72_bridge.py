"""
CORTEX A-72 NEURAL BRIDGE
-------------------------
The central synaptic interface for IQ4_NL.
Routes all intelligence from NET/LAN layers to the Logic Layer
and distributes residual data to the rest of the system.
"""

import time
import hashlib
import json
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class SignalPriority(Enum):
    CRITICAL = 1  # Direct to Logic Layer
    HIGH = 2      # To Logic + Visualization
    NORMAL = 3    # To Visualization/DB only
    NOISE = 4     # Discard

@dataclass
class NeuralPacket:
    source: str  # 'NET' or 'LAN'
    raw_data: Dict[str, Any]
    timestamp: float
    signature: str
    
class CortexA72Bridge:
    def __init__(self):
        self.synaptic_weights = {
            'elliptical_factor': 0.85,
            'seismic_threshold': 0.02,
            'logic_gate_open': True
        }
        self.logic_layer_callback: Optional[Callable] = None
        self.system_broadcast_callback: Optional[Callable] = None
        print("🧠 CORTEX A-72: Neural Bridge Initialized")
        print("   Waiting for IQ4_NL input streams...")

    def connect_logic_layer(self, callback: Callable):
        """Connects the bridge directly to the User's Logic Layer."""
        self.logic_layer_callback = callback
        print("✅ CORTEX A-72: Direct Neural Link to LOGIC LAYER established.")

    def connect_system_rest(self, callback: Callable):
        """Connects to the rest of the systems (DB, Vis, etc)."""
        self.system_broadcast_callback = callback

    def ingest_iq4_nl(self, source: str, data: Dict[str, Any]) -> None:
        """
        Main entry point for IQ4_NL packets from NET or LAN.
        """
        packet = self._create_packet(source, data)
        
        # 1. Synaptic Processing (Transformation)
        processed_signal = self._synaptic_transform(packet)
        
        # 2. Priority Classification
        priority = self._classify_priority(processed_signal)
        
        # 3. Routing
        self._route_signal(packet, processed_signal, priority)

    def _create_packet(self, source: str, data: Dict[str, Any]) -> NeuralPacket:
        sig_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:8]
        return NeuralPacket(
            source=source,
            raw_data=data,
            timestamp=time.time(),
            signature=sig_hash
        )

    def _synaptic_transform(self, packet: NeuralPacket) -> Dict[str, Any]:
        """
        Applies Elliptical and Seismic transformations to raw data.
        This is where the 'Geographing' and 'Seismographing' happen.
        """
        raw = packet.raw_data
        transformed = raw.copy()
        
        # Apply Elliptical Projection (Simulated)
        if 'ra' in raw and 'dec' in raw:
            ra, dec = raw['ra'], raw['dec']
            # Simple elliptical projection logic
            ex = ra * (1.0 - self.synaptic_weights['elliptical_factor'] * (dec / 90.0)**2)
            ey = dec * self.synaptic_weights['elliptical_factor']
            transformed['elliptical_x'] = ex
            transformed['elliptical_y'] = ey
            
        # Apply Seismic Wave Analysis (Simulated)
        if 'intensity' in raw:
            seismic_val = raw['intensity'] * self.synaptic_weights['seismic_threshold']
            transformed['seismic_wave'] = seismic_val
            transformed['is_quake'] = abs(seismic_val) > 0.5
            
        return transformed

    def _classify_priority(self, signal: Dict[str, Any]) -> SignalPriority:
        if signal.get('is_quake'):
            return SignalPriority.CRITICAL
        if signal.get('elliptical_x') and signal.get('elliptical_y'):
            return SignalPriority.HIGH
        if 'noise' in signal:
            return SignalPriority.NOISE
        return SignalPriority.NORMAL

    def _route_signal(self, packet: NeuralPacket, signal: Dict[str, Any], priority: SignalPriority):
        """
        Routes the signal based on priority.
        CRITICAL/HIGH -> Logic Layer
        ALL (except NOISE) -> Rest of System
        """
        if priority == SignalPriority.NOISE:
            return

        # Prepare the payload for the Logic Layer
        logic_payload = {
            "type": "IQ_DIRECT",
            "source": packet.source,
            "priority": priority.name,
            "data": signal,
            "cortex_id": "A-72"
        }

        # 1. Send to Logic Layer (The Bridge's primary function)
        if priority in [SignalPriority.CRITICAL, SignalPriority.HIGH] and self.logic_layer_callback:
            self.logic_layer_callback(logic_payload)
            
        # 2. Broadcast to Rest of System (Visualization, Storage, etc.)
        if self.system_broadcast_callback:
            self.system_broadcast_callback({
                "type": "SYSTEM_UPDATE",
                "data": signal,
                "pictography": self._generate_pictography(signal)
            })

    def _generate_pictography(self, signal: Dict[str, Any]) -> str:
        intensity = signal.get('seismic_wave', 0)
        if abs(intensity) > 0.8: return "⚡🌌"
        if abs(intensity) > 0.4: return "✨"
        if abs(intensity) > 0.1: return "·"
        return "-"

# --- Demo Usage ---
if __name__ == "__main__":
    def my_logic_receiver(payload):
        print(f"\n🧠 [LOGIC LAYER] Received IQ Direct: {payload['priority']} from {payload['source']}")
        print(f"   Data: RA={payload['data'].get('ra')}, Elliptical X={payload['data'].get('elliptical_x')}")

    def system_receiver(payload):
        print(f"📡 [SYSTEM REST] Update: {payload['pictography']}")

    # Initialize Bridge
    cortex = CortexA72Bridge()
    cortex.connect_logic_layer(my_logic_receiver)
    cortex.connect_system_rest(system_receiver)

    print("\n--- Simulating IQ4_NL Input Streams ---")
    
    # Simulate LAN Input (Local Config)
    lan_data = {"ra": 266.4, "dec": -29.0, "intensity": 0.9, "source_config": "user_local"}
    cortex.ingest_iq4_nl("LAN", lan_data)
    
    # Simulate NET Input (Remote Secure)
    net_data = {"ra": 192.0, "dec": 45.0, "intensity": 0.2, "source_config": "nx_secure"}
    cortex.ingest_iq4_nl("NET", net_data)
    
    # Simulate Noise
    noise_data = {"noise": True, "junk": 123}
    cortex.ingest_iq4_nl("NET", noise_data)

    print("\n✅ Cortex A-72 Cycle Complete.")
