
"""
NEURON BRIDGE -- FXION Master Config Loader
Parses Unified Omega Mode configuration.
"""
import configparser
import os

class NeuronBridge:
    def __init__(self, config_path="fxion_omega_unified.cfg"):
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file {config_path} not found.")
        self.config.read(config_path)
        self.version = self.config.get("NEURON_BRIDGE", "version", fallback="8.712")

    def get_section(self, section):
        if self.config.has_section(section):
            return dict(self.config.items(section))
        return {}

    def get_topology(self):
        return self.get_section("TOPOLOGY")

    def get_pipeline(self):
        return self.get_section("FXIONBTC_PIPELINE")

    def get_split_config(self):
        return self.get_section("PHANTOM_SPLIT")

if __name__ == "__main__":
    nb = NeuronBridge()
    print(f"Loaded NeuronBridge v{nb.version}")
    print(f"Pipeline Layers: {len(nb.get_pipeline())}")
