"""
FXION -- PCIe GPU Engine Module
Q8 Augmented Quantization | CUDA Kernel Interface | UCB1 RL Policy
"""
from fxion.engine import FXIONEngine
from fxion.quantizer import FXIONQuantizer
from fxion.pcie import PCIeBridge

__all__ = ["FXIONEngine", "FXIONQuantizer", "PCIeBridge"]
__version__ = "1.0.0"
