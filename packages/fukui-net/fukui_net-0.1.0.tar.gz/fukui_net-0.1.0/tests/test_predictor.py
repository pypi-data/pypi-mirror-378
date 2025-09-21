"""
Tests for FukuiNetPredictor class.
"""

import os

import pytest
import torch

from fukui_net.predictor import FukuiNetPredictor


class TestFukuiNetPredictor:
    """Test cases for FukuiNetPredictor."""

    @pytest.fixture
    def predictor(self):
        """Create a predictor instance for testing."""
        checkpoint_path = "models/final_model.ckpt"
        if not os.path.exists(checkpoint_path):
            pytest.skip("Model checkpoint not found")
        return FukuiNetPredictor(checkpoint_path, device="cpu")

    def test_predictor_initialization(self, predictor):
        """Test that predictor initializes correctly."""
        assert predictor is not None
        assert predictor.device.type == 'cpu'
        assert predictor.model is not None

    def test_predict_single_molecule(self, predictor):
        """Test prediction for a single molecule."""
        smiles = "CCO"  # Ethanol
        predictions = predictor.predict_smiles(smiles)

        assert isinstance(predictions, list)
        assert len(predictions) > 0
        assert all(isinstance(p, float) for p in predictions)
        # Ethanol has 9 atoms (with hydrogens)
        assert len(predictions) == 9

    def test_predict_batch(self, predictor):
        """Test batch prediction."""
        smiles_list = ["CCO", "c1ccccc1"]  # Ethanol and Benzene
        predictions = predictor.predict_batch(smiles_list)

        assert isinstance(predictions, list)
        assert len(predictions) == 2
        assert all(isinstance(mol_preds, list) for mol_preds in predictions)
        assert all(isinstance(val, float) for mol_preds in predictions for val in mol_preds)

    def test_predict_from_csv(self, predictor, tmp_path):
        """Test prediction from CSV file."""
        # Create test CSV
        import pandas as pd
        test_data = pd.DataFrame({
            'smiles': ['CCO', 'c1ccccc1'],
            'name': ['Ethanol', 'Benzene']
        })
        input_file = tmp_path / "test_input.csv"
        output_file = tmp_path / "test_output.csv"
        test_data.to_csv(input_file, index=False)

        # Run prediction
        predictor.predict_from_csv(str(input_file), str(output_file), smiles_column='smiles')

        # Check output
        assert output_file.exists()
        output_data = pd.read_csv(output_file)
        assert len(output_data) == 2
        assert 'smiles' in output_data.columns
        assert 'fukui_indices' in output_data.columns
        assert output_data['smiles'].tolist() == ['CCO', 'c1ccccc1']

    def test_different_devices(self):
        """Test predictor with different devices."""
        checkpoint_path = "models/final_model.ckpt"
        if not os.path.exists(checkpoint_path):
            pytest.skip("Model checkpoint not found")

        # Test CPU
        predictor_cpu = FukuiNetPredictor(checkpoint_path, device="cpu")
        assert predictor_cpu.device.type == 'cpu'

        # Test CUDA if available
        if torch.cuda.is_available():
            predictor_cuda = FukuiNetPredictor(checkpoint_path, device="cuda:1")
            assert predictor_cuda.device.type == 'cuda'
            assert predictor_cuda.device.index == 1

    def test_invalid_smiles(self, predictor):
        """Test prediction with invalid SMILES."""
        with pytest.raises((ValueError, RuntimeError)):
            predictor.predict_smiles("invalid_smiles")

    def test_empty_batch(self, predictor):
        """Test prediction with empty batch."""
        predictions = predictor.predict_batch([])
        assert predictions == []

