"""
NEURON BRIDGE Configuration Loader
Parses NeuronBridge_8.712_*.cfg INI-style configuration into structured dict.
"""
import os
import configparser
from pathlib import Path


CFG_PATH = Path(__file__).parent / "neuronbridge.cfg"


def load_config(path: str = None) -> dict:
    cfg_path = Path(path) if path else CFG_PATH
    if not cfg_path.exists():
        return {"error": f"config not found: {cfg_path}"}
    parser = configparser.ConfigParser()
    parser.read(cfg_path)
    out = {}
    for section in parser.sections():
        out[section] = dict(parser.items(section))
    return out


def summary() -> dict:
    cfg = load_config()
    topo = cfg.get("TOPOLOGY", {})
    quant = cfg.get("QUANTIZATION", {})
    speed = cfg.get("SPEED_MODE", {})
    heal = cfg.get("SELF_HEAL", {})
    bridge = cfg.get("NEURON_BRIDGE", {})
    return {
        "version": bridge.get("version", "8.712"),
        "layers": int(topo.get("layers", 12)),
        "bridges_per_layer": int(topo.get("bridges_per_layer", 12)),
        "qbits_total": int(topo.get("qbits_total", 0)),
        "primary_quant": quant.get("primary_quant", "Q8_0"),
        "fallback_quant": quant.get("fallback_quant", "Q4_K_M"),
        "iq_variants": quant.get("iq_variants", "").split(","),
        "target_tps": int(speed.get("target_tps", 0)),
        "target_qps": int(speed.get("target_qps", 0)),
        "clock_lock_mhz": int(speed.get("clock_lock_mhz", 0)),
        "self_heal_enabled": heal.get("enabled", "true") == "true",
        "max_seq_len": int(bridge.get("max_seq_len", 8192)),
        "attention_heads": int(bridge.get("attention_heads", 32)),
        "flash_attention": bridge.get("flash_attention", "true") == "true",
        "sections": list(cfg.keys()),
    }
