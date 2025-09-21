"""
Hugging Face Transformers integration for FukuiNet (root level)
"""

from fukui_net.hf_integration import FukuiNetConfig, FukuiNetForMolecularProperty

# Re-export for transformers to find
__all__ = ["FukuiNetConfig", "FukuiNetForMolecularProperty"]
