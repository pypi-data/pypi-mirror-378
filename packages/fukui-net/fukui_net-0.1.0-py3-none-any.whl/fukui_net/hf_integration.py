"""
Hugging Face Transformers integration for FukuiNet

This module provides Hugging Face compatible classes for FukuiNet model.
"""

import os
from typing import Any

import torch
from transformers import PretrainedConfig, PreTrainedModel
from transformers.utils import logging

from fukui_net.predictor import FukuiNetPredictor

logger = logging.get_logger(__name__)


class FukuiNetConfig(PretrainedConfig):
    """
    Configuration class for FukuiNet model.

    This class holds the configuration for FukuiNet model parameters.
    """

    model_type = "fukui_net"

    def __init__(
        self,
        atom_in_features: int = 133,
        edge_attr_dim: int = 14,
        hidden_dim: int = 128,
        kan_grid_size: int = 5,
        kan_spline_order: int = 3,
        cheb_k: int = 3,
        num_layers: int = 3,
        dropout: float = 0.1,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.atom_in_features = atom_in_features
        self.edge_attr_dim = edge_attr_dim
        self.hidden_dim = hidden_dim
        self.kan_grid_size = kan_grid_size
        self.kan_spline_order = kan_spline_order
        self.cheb_k = cheb_k
        self.num_layers = num_layers
        self.dropout = dropout


class FukuiNetForMolecularProperty(PreTrainedModel):
    """
    Hugging Face compatible wrapper for FukuiNet model.

    This class wraps the FukuiNet predictor to make it compatible with
    Hugging Face Transformers AutoModel interface.
    """

    config_class = FukuiNetConfig

    def __init__(self, config: FukuiNetConfig):
        super().__init__(config)
        self.config = config
        self.predictor = None

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, *model_args, **kwargs):
        """Override from_pretrained to handle our custom checkpoint format."""
        # Load config first
        config = kwargs.pop("config", None)
        if config is None:
            config = FukuiNetConfig.from_pretrained(pretrained_model_name_or_path, **kwargs)

        # Create model instance
        model = cls(config)

        # Load our custom checkpoint
        checkpoint_path = os.path.join(pretrained_model_name_or_path, "models/final_model.ckpt")
        if not os.path.exists(checkpoint_path):
            checkpoint_path = "models/final_model.ckpt"  # fallback

        if os.path.exists(checkpoint_path):
            device = kwargs.get("device", "auto")
            model.from_pretrained_checkpoint(checkpoint_path, device=device)

        return model

    def from_pretrained_checkpoint(self, checkpoint_path: str, device: str = "auto"):
        """
        Load model from FukuiNet checkpoint.

        Args:
            checkpoint_path: Path to the model checkpoint file
            device: Device to run inference on ('cpu', 'cuda', 'cuda:1', etc.)
        """
        self.predictor = FukuiNetPredictor(checkpoint_path, device)
        return self

    def predict(self, smiles: str | list[str]) -> list[float] | list[list[float]]:
        """
        Predict Fukui indices for SMILES.

        Args:
            smiles: SMILES string or list of SMILES strings

        Returns:
            Fukui indices as list of floats or list of lists
        """
        if self.predictor is None:
            raise ValueError("Model not loaded. Use from_pretrained_checkpoint() first.")

        if isinstance(smiles, str):
            return self.predictor.predict_smiles(smiles)
        else:
            return [self.predictor.predict_smiles(s) for s in smiles]

    def predict_batch(self, smiles_list: list[str]) -> list[list[float]]:
        """
        Predict Fukui indices for a batch of SMILES.

        Args:
            smiles_list: List of SMILES strings

        Returns:
            List of Fukui indices for each molecule
        """
        if self.predictor is None:
            raise ValueError("Model not loaded. Use from_pretrained_checkpoint() first.")

        return self.predictor.predict_batch(smiles_list)

    def forward(self, input_ids: torch.Tensor, **kwargs) -> dict[str, Any]:
        """
        Forward pass for Hugging Face compatibility.

        This method is required by PreTrainedModel but not used directly.
        Use predict() method instead.
        """
        raise NotImplementedError(
            "Use predict() method instead. This model works with SMILES strings, not tokenized inputs."
        )


# Manual registration function for external use
def register_fukui_net():
    """Register FukuiNet model classes with transformers AutoModel."""
    try:
        from transformers import AutoConfig, AutoModel

        AutoConfig.register("fukui_net", FukuiNetConfig)
        AutoModel.register(FukuiNetConfig, FukuiNetForMolecularProperty)

        logger.info("Successfully registered FukuiNet with transformers AutoModel")
        return True
    except Exception as e:
        logger.warning(f"Could not register FukuiNet with transformers: {e}")
        return False
