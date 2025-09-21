"""
FukuiNet: Neural Network for Predicting Fukui Indices
"""

from fukui_net.hf_integration import FukuiNetConfig, FukuiNetForMolecularProperty
from fukui_net.predictor import FukuiNetPredictor

__version__ = "0.1.0"
__all__ = [
    "FukuiNetPredictor",
    "FukuiNetConfig",
    "FukuiNetForMolecularProperty"
]
