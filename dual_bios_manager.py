
"""
FXION DUAL BIOS MANAGER -- Redundancy & Stability Control
Manages BIOS A (Performance) and BIOS B (Stability) switching.
"""
import logging
import os

log = logging.getLogger("DUAL_BIOS")

class DualBIOSManager:
    def __init__(self, config):
        self.enabled = config.get("enabled", "true") == "true"
        self.active = config.get("active_bios", "BIOS_A")
        self.bios_a = config.get("bios_a_name", "OMEGA_TURBO")
        self.bios_b = config.get("bios_b_name", "STABLE_SAFE")
        self.auto_fallback = config.get("auto_fallback", "true") == "true"
        
        log.info(f"Dual BIOS System: {'ENABLED' if self.enabled else 'DISABLED'}")
        log.info(f"Current Active BIOS: {self.active} ({self.bios_a if self.active == 'BIOS_A' else self.bios_b})")

    def switch_bios(self):
        """Switches between BIOS A and BIOS B."""
        old_bios = self.active
        self.active = "BIOS_B" if self.active == "BIOS_A" else "BIOS_A"
        new_name = self.bios_a if self.active == "BIOS_A" else self.bios_b
        log.warning(f"DUAL BIOS SWITCH: {old_bios} -> {self.active} ({new_name})")
        return self.active

    def verify_integrity(self, psi_coherence):
        """Triggers fallback if coherence is too low."""
        if self.auto_fallback and psi_coherence < 0.90 and self.active == "BIOS_A":
            log.error("CRITICAL INSTABILITY DETECTED in BIOS_A. Falling back to BIOS_B (Safe Mode)...")
            return self.switch_bios()
        return self.active

if __name__ == "__main__":
    from neuron_bridge import NeuronBridge
    nb = NeuronBridge()
    db = DualBIOSManager(nb.get_section("DUAL_BIOS"))
    print(f"Active BIOS: {db.active}")
