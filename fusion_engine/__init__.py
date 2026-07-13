"""
Fusion Engine - Core Package
Advanced 6-bit entropy fusion engine with negative latency prediction
"""

__version__ = "1.0.0"
__author__ = "Fusion Engine Team"

from .core.sqrt_engine import SixBySixSqrtEngine
from .core.quantization import QuantizedEntropyEngine
from .core.fusion_core import FusionCoreEngine
from .cache.waylink import WayLinkCacheHierarchy
from .cache.ccx_optimizer import CCXOptimizer
from .crypto.merkle_turbo import MerkleTurboValidator
from .crypto.sha384_xor import SHA384XORMixer
from .network.bandwidth_manager import BandwidthManager
from .network.vram_split import VRAMSplitManager
from .utils.plank_force import PlankForcePredictor
from .utils.golden_circle import GoldenCircleRatio

__all__ = [
    "SixBySixSqrtEngine",
    "QuantizedEntropyEngine",
    "FusionCoreEngine",
    "WayLinkCacheHierarchy",
    "CCXOptimizer",
    "MerkleTurboValidator",
    "SHA384XORMixer",
    "BandwidthManager",
    "VRAMSplitManager",
    "PlankForcePredictor",
    "GoldenCircleRatio",
]
