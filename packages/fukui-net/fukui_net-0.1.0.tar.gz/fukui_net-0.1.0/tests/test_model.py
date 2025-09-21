"""
Tests for model architecture and utilities.
"""

import torch

from fukui_net.utils.efficient_kan import KAN, KANLinear
from fukui_net.utils.prepare import FeaturizationParameters, MoleculeData
from fukui_net.utils.train import Model


class TestModelComponents:
    """Test cases for model components."""

    def test_kan_linear(self):
        """Test KANLinear layer."""
        layer = KANLinear(in_features=10, out_features=5)
        x = torch.randn(3, 10)
        output = layer(x)

        assert output.shape == (3, 5)
        assert not torch.isnan(output).any()

    def test_kan_network(self):
        """Test KAN network."""
        kan = KAN(layers_hidden=[10, 20, 5])
        x = torch.randn(3, 10)
        output = kan(x)

        assert output.shape == (3, 5)
        assert not torch.isnan(output).any()

    def test_featurization_parameters(self):
        """Test FeaturizationParameters."""
        params = FeaturizationParameters()

        assert params.max_atomic_num == 100
        assert params.atom_fdim > 0
        assert 'atomic_num' in params.atom_features
        assert 'degree' in params.atom_features

    def test_molecule_data(self):
        """Test MoleculeData class."""
        smiles = "CCO"
        target = [0.1, 0.2, 0.3]

        mol_data = MoleculeData(smiles, target)

        assert mol_data.smiles == smiles
        assert mol_data.target.shape == (3,)
        assert mol_data.mol is not None
        assert mol_data.edge_index.shape[0] == 2
        assert mol_data.edge_attr.shape[1] == 10  # BOND_FDIM

    def test_model_architecture(self):
        """Test Model architecture."""
        model = Model(
            atom_in_features=133,
            edge_attr_dim=14,
            preprocess_hidden_features=[128] * 2,
            cheb_hidden_features=[128, 64],
            K=[3, 2],
            cheb_normalizations=["sym", "sym"],
            dropout_rates=[0.1, 0.1, 0.1, 0.1],
            activation_fns=[torch.nn.ReLU] * 4,
            use_batch_norm=[True] * 4,
            postprocess_hidden_features=[64, 32],
            out_features=1
        )

        # Test forward pass with dummy data
        num_atoms = 10

        x = torch.randn(num_atoms, 133)
        edge_index = torch.randint(0, num_atoms, (2, 20))
        edge_attr = torch.randn(20, 14)

        output = model(x, edge_index, edge_attr)

        assert output.shape == (num_atoms,)
        assert not torch.isnan(output).any()


class TestDataProcessing:
    """Test cases for data processing utilities."""

    def test_onek_encoding(self):
        """Test one-hot encoding function."""
        from fukui_net.utils.prepare import onek_encoding_unk

        choices = [0, 1, 2, 3]

        # Test valid value
        encoding = onek_encoding_unk(2, choices)
        assert encoding == [0, 0, 1, 0, 0]  # +1 for unknown

        # Test unknown value
        encoding = onek_encoding_unk(5, choices)
        assert encoding == [0, 0, 0, 0, 1]  # Unknown at the end

    def test_bond_features(self):
        """Test bond feature generation."""
        from rdkit import Chem

        from fukui_net.utils.prepare import bond_features

        # Create a simple molecule
        mol = Chem.MolFromSmiles("CCO")
        bonds = mol.GetBonds()

        if bonds:
            bond = bonds[0]
            features = bond_features(bond)
            assert len(features) == 10  # BOND_FDIM
            assert all(isinstance(f, (int, float, bool)) for f in features)

    def test_atom_features(self):
        """Test atom feature generation."""
        from rdkit import Chem

        from fukui_net.utils.prepare import atom_features

        # Create a simple molecule
        mol = Chem.MolFromSmiles("CCO")
        atoms = mol.GetAtoms()

        if atoms:
            atom = atoms[0]
            params = FeaturizationParameters()
            features = atom_features(atom, params)
            assert len(features) == params.atom_fdim
            assert all(isinstance(f, (int, float, bool)) for f in features)

