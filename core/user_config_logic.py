"""
USER CONFIG LOGIC ENGINE
------------------------
Your personal configuration logic receiver.
Connected directly via LAN Layer (IQ_DIRECT).
"""

import sys
sys.path.insert(0, '/workspace')

from core.iq4_nl_protocol import IQ4NLController, LinkType, Packet

class MyConfigLogic:
    """
    YOUR PERSONAL CONFIGURATION LOGIC
    Receives direct IQ injections from LAN layer.
    """
    def __init__(self):
        self.config_state = {
            "elliptical_mode": False,
            "seismo_threshold": 0.5,
            "quantum_entanglement": False,
            "galaxy_map_loaded": False
        }
        
    def apply_config(self, data: dict):
        """Apply incoming IQ parameters to your logic."""
        print("\n" + "="*40)
        print("🧠 CONFIG LOGIC PROCESSING")
        print("="*40)
        
        if "elliptical_angle" in data:
            self.config_state["elliptical_mode"] = True
            print(f"✓ Elliptical Angle Set: {data['elliptical_angle']}°")
            
        if "seismo_gain" in data:
            print(f"✓ Seismograph Gain: {data['seismo_gain']}x")
            
        if "quantum_state" in data:
            if data["quantum_state"] == "ENTANGLED":
                self.config_state["quantum_entanglement"] = True
                print(f"⚡ QUANTUM STATE: ENTANGLED")
                
        if "star_map_region" in data:
            self.config_state["galaxy_map_loaded"] = True
            print(f"🌌 Star Map Region: {data['star_map_region']}")
            
        print(f"\nCurrent State: {self.config_state}")
        print("="*40 + "\n")
        return self.config_state

def main():
    # Initialize your config logic
    my_logic = MyConfigLogic()
    
    # Initialize IQ4_NL Controller
    # NET points to NX Secure Server (external)
    # LAN handles local injection
    controller = IQ4NLController(nx_host="nx.secure.local", nx_port=9999)
    
    # Register YOUR config logic on the LAN layer
    controller.lan_layer.register_logic("user_config_main", my_logic.apply_config)
    
    print("\n🚀 IQ4_NL PROTOCOL ACTIVE")
    print("   NET Layer: Ready for NX Secure Server")
    print("   LAN Layer: Direct IQ Injection Enabled")
    print("   Target Logic: user_config_main\n")
    
    # Simulate receiving commands
    test_packets = [
        # LAN Packet - Direct Config
        controller.create_lan_packet(
            target="user_config_main",
            data={"elliptical_angle": 60.0, "seismo_gain": 1.5}
        ),
        # IQ_DIRECT Packet - Quantum Override
        Packet(
            header="QUANTUM_OVERRIDE",
            link_type=LinkType.IQ_DIRECT,
            payload={"target_logic": "user_config_main", "quantum_state": "ENTANGLED"}
        ),
        # LAN Packet - Star Map
        controller.create_lan_packet(
            target="user_config_main",
            data={"star_map_region": "MILKY_WAY_CORE", "elliptical_angle": 62.5}
        )
    ]
    
    for pkt in test_packets:
        controller.route_packet(pkt)
        
    print("\n✅ All packets routed successfully.")
    print("   NET traffic would go to NX Secure Server")
    print("   LAN traffic processed by your config logic")

if __name__ == "__main__":
    main()
