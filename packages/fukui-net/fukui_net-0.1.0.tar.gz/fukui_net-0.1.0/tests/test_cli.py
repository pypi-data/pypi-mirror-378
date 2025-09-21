"""
Tests for CLI functionality.
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCLI:
    """Test cases for CLI commands."""

    def test_info_command(self):
        """Test the info command."""
        result = subprocess.run(
            [sys.executable, "-m", "fukui_net", "info"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 0
        assert "Available Devices" in result.stdout
        assert "Model checkpoint found" in result.stdout or "Model checkpoint not found" in result.stdout

    def test_predict_single_molecule(self):
        """Test single molecule prediction."""
        result = subprocess.run(
            [sys.executable, "-m", "fukui_net", "predict", "CCO", "--device", "cpu"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 0
        assert "Model loaded successfully" in result.stdout
        assert "Fukui indices:" in result.stdout

    def test_predict_batch_csv(self):
        """Test batch prediction from CSV."""
        input_file = Path(__file__).parent / "data" / "test_molecules.csv"
        output_file = Path(__file__).parent / "data" / "test_predictions.csv"

        if not input_file.exists():
            pytest.skip("Test data file not found")

        result = subprocess.run(
            [
                sys.executable, "-m", "fukui_net", "predict",
                "--csv", str(input_file),
                "--output", str(output_file),
                "--device", "cpu"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 0
        assert "Model loaded successfully" in result.stdout
        assert "Predictions saved to" in result.stdout
        assert output_file.exists()

    def test_missing_arguments(self):
        """Test CLI with missing arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "fukui_net", "predict"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 1
        assert "Please provide either SMILES string or --csv file" in result.stdout

    def test_csv_without_output(self):
        """Test CSV prediction without output file."""
        input_file = Path(__file__).parent / "data" / "test_molecules.csv"

        if not input_file.exists():
            pytest.skip("Test data file not found")

        result = subprocess.run(
            [
                sys.executable, "-m", "fukui_net", "predict",
                "--csv", str(input_file),
                "--device", "cpu"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 1
        assert "--output is required when using --csv" in result.stdout

