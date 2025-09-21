"""
Tests for Hugging Face Transformers integration
"""

import pytest
from transformers import AutoConfig, AutoModel

from fukui_net.hf_integration import FukuiNetConfig, FukuiNetForMolecularProperty
from fukui_net.pipeline import FukuiIndexPredictionPipeline, fukui_index_pipeline


class TestFukuiNetConfig:
    """Test FukuiNetConfig class."""

    def test_config_creation(self):
        """Test config creation with default parameters."""
        config = FukuiNetConfig()

        assert config.model_type == "fukui_net"
        assert config.atom_in_features == 133
        assert config.edge_attr_dim == 14
        assert config.hidden_dim == 128
        assert config.kan_grid_size == 5
        assert config.kan_spline_order == 3
        assert config.cheb_k == 3
        assert config.num_layers == 3
        assert config.dropout == 0.1

    def test_config_custom_parameters(self):
        """Test config creation with custom parameters."""
        config = FukuiNetConfig(
            atom_in_features=150,
            hidden_dim=256,
            num_layers=5
        )

        assert config.atom_in_features == 150
        assert config.hidden_dim == 256
        assert config.num_layers == 5
        # Other parameters should remain default
        assert config.edge_attr_dim == 14
        assert config.dropout == 0.1


class TestFukuiNetForMolecularProperty:
    """Test FukuiNetForMolecularProperty class."""

    def test_model_creation(self):
        """Test model creation."""
        config = FukuiNetConfig()
        model = FukuiNetForMolecularProperty(config)

        assert model.config == config
        assert model.predictor is None

    def test_model_without_checkpoint(self):
        """Test model methods without loaded checkpoint."""
        config = FukuiNetConfig()
        model = FukuiNetForMolecularProperty(config)

        # Should raise error when predictor not loaded
        with pytest.raises(ValueError, match="Model not loaded"):
            model.predict("CCO")

        with pytest.raises(ValueError, match="Model not loaded"):
            model.predict_batch(["CCO", "c1ccccc1"])

    @pytest.mark.integration
    def test_model_with_checkpoint(self):
        """Test model with checkpoint loading."""
        config = FukuiNetConfig()
        model = FukuiNetForMolecularProperty(config)

        # This test requires the actual checkpoint file
        import os
        checkpoint_path = "models/final_model.ckpt"

        if os.path.exists(checkpoint_path):
            model.from_pretrained_checkpoint(checkpoint_path, device="cpu")

            # Test prediction
            result = model.predict("CCO")
            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(x, (int, float)) for x in result)

            # Test batch prediction
            results = model.predict_batch(["CCO", "c1ccccc1"])
            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(r, list) for r in results)


class TestAutoModelRegistration:
    """Test AutoModel registration."""

    def test_auto_config_registration(self):
        """Test that FukuiNetConfig is registered with AutoConfig."""
        config = AutoConfig.from_pretrained(
            ".",  # Use local config
            trust_remote_code=True
        )

        assert isinstance(config, FukuiNetConfig)
        assert config.model_type == "fukui_net"

    def test_auto_model_registration(self):
        """Test that FukuiNetForMolecularProperty is registered with AutoModel."""
        model = AutoModel.from_pretrained(
            ".",  # Use local config
            trust_remote_code=True
        )

        assert isinstance(model, FukuiNetForMolecularProperty)
        assert model.config.model_type == "fukui_net"


class TestFukuiIndexPredictionPipeline:
    """Test FukuiIndexPredictionPipeline class."""

    def test_pipeline_creation(self):
        """Test pipeline creation."""
        config = FukuiNetConfig()
        model = FukuiNetForMolecularProperty(config)

        pipeline = FukuiIndexPredictionPipeline(model=model)

        assert pipeline.model == model

    def test_pipeline_preprocessing(self):
        """Test pipeline preprocessing."""
        config = FukuiNetConfig()
        model = FukuiNetForMolecularProperty(config)
        pipeline = FukuiIndexPredictionPipeline(model=model)

        # Test single SMILES
        result = pipeline.preprocess("CCO")
        assert "smiles" in result
        assert result["smiles"] == ["CCO"]

        # Test multiple SMILES
        result = pipeline.preprocess(["CCO", "c1ccccc1"])
        assert result["smiles"] == ["CCO", "c1ccccc1"]

        # Test invalid input
        with pytest.raises(ValueError):
            pipeline.preprocess("")

        with pytest.raises(ValueError):
            pipeline.preprocess([""])


class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.mark.integration
    def test_complete_workflow(self):
        """Test complete workflow from config to prediction."""
        import os

        checkpoint_path = "models/final_model.ckpt"
        if not os.path.exists(checkpoint_path):
            pytest.skip("Model checkpoint not found")

        # Load config
        config = AutoConfig.from_pretrained(".", trust_remote_code=True)
        assert isinstance(config, FukuiNetConfig)

        # Load model
        model = AutoModel.from_pretrained(".", trust_remote_code=True)
        assert isinstance(model, FukuiNetForMolecularProperty)

        # Load checkpoint
        model.from_pretrained_checkpoint(checkpoint_path, device="cpu")

        # Test prediction
        result = model.predict("CCO")
        assert isinstance(result, list)
        assert len(result) > 0

        # Test batch prediction
        results = model.predict_batch(["CCO", "c1ccccc1"])
        assert len(results) == 2
        assert all(isinstance(r, list) for r in results)

    @pytest.mark.integration
    def test_pipeline_workflow(self):
        """Test pipeline workflow."""
        import os

        checkpoint_path = "models/final_model.ckpt"
        if not os.path.exists(checkpoint_path):
            pytest.skip("Model checkpoint not found")

        # Create pipeline
        pipeline = fukui_index_pipeline(
            model_name_or_path=".",
            checkpoint_path=checkpoint_path,
            device="cpu"
        )

        # Test prediction
        result = pipeline("CCO")

        assert "fukui_indices" in result
        assert "smiles" in result
        assert "num_atoms" in result
        assert "most_electrophilic_atom" in result
        assert "most_nucleophilic_atom" in result
        assert "reactivity_range" in result
        assert "reactivity_analysis" in result

        # Test batch prediction
        results = pipeline(["CCO", "c1ccccc1"])
        assert isinstance(results, list)
        assert len(results) == 2
