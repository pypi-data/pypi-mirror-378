"""
Fukui_Net Predictor Module

This module contains the FukuiNetPredictor class for predicting Fukui indices.
"""


import pandas as pd
import torch
from torch_geometric.loader import DataLoader

from fukui_net.utils.prepare import FeaturizationParameters, MoleculeDataset
from fukui_net.utils.train import Model, MoleculeModel


class FukuiNetPredictor:
    """
    A class for predicting Fukui indices using the trained Fukui_Net model.
    """

    def __init__(self, checkpoint_path: str, device: str = "auto"):
        """
        Initialize the FukuiNetPredictor.

        Args:
            checkpoint_path (str): Path to the model checkpoint file.
            device (str): Device to run inference on ('cpu', 'cuda', 'cuda:1', etc.).
        """
        self.checkpoint_path = checkpoint_path
        self.device = self._setup_device(device)
        self.model = self._load_model()
        self.params = FeaturizationParameters()

    def _setup_device(self, device: str) -> torch.device:
        """Setup the device for inference."""
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda:1"  # Default to GPU card 1
                # Clear CUDA cache
                torch.cuda.empty_cache()
            else:
                device = "cpu"

        return torch.device(device)

    def _load_model(self) -> MoleculeModel:
        """Load the trained model from checkpoint."""
        # Load the checkpoint
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)

        # Extract hyperparameters
        hparams = checkpoint.get('hyper_parameters', {})

        # Use the exact architecture from the original training
        # These values are inferred from the checkpoint dimensions
        atom_in_features = 133  # From checkpoint: residual.weight shape [128, 133]
        edge_attr_dim = 14  # From checkpoint: interaction input 147 = 133 + 14
        preprocess_hidden_features = [128] * 9  # From model.py
        cheb_hidden_features = [128, 128]  # From model.py
        K = [10, 16]  # From model.py
        cheb_normalizations = ["sym", "sym"]  # From model.py
        dropout_rates = [0.0] * (len(preprocess_hidden_features) + 2)  # From model.py
        activation_fns = [torch.nn.PReLU] * (len(preprocess_hidden_features) + 2)  # From model.py
        use_batch_norm = [True] * (len(preprocess_hidden_features) + 2)  # From model.py
        postprocess_hidden_features = [128, 128]  # From model.py
        out_features = 1  # From model.py

        # Create the model backbone with the same architecture
        model_backbone = Model(
            atom_in_features=atom_in_features,
            edge_attr_dim=edge_attr_dim,
            preprocess_hidden_features=preprocess_hidden_features,
            cheb_hidden_features=cheb_hidden_features,
            K=K,
            cheb_normalizations=cheb_normalizations,
            dropout_rates=dropout_rates,
            activation_fns=activation_fns,
            use_batch_norm=use_batch_norm,
            postprocess_hidden_features=postprocess_hidden_features,
            out_features=out_features
        )

        # Create the Lightning module
        model = MoleculeModel(
            model_backbone=model_backbone,
            optimizer_class=torch.optim.Adam,
            learning_rate=hparams.get('learning_rate', 1e-3),
            weight_decay=hparams.get('weight_decay', 1e-5),
            step_size=hparams.get('step_size', 50),
            gamma=hparams.get('gamma', 0.5),
            batch_size=hparams.get('batch_size', 32),
            metric=hparams.get('metric', 'rmse')
        )

        # Load only the model backbone weights (skip optimizer states)
        model_state_dict = {}
        for key, value in checkpoint['state_dict'].items():
            if key.startswith('model_backbone.'):
                new_key = key.replace('model_backbone.', '')
                model_state_dict[new_key] = value

        # Load the weights into the backbone
        model_backbone.load_state_dict(model_state_dict)
        model.eval()
        model.to(self.device)

        # Clear CUDA cache after model loading
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()

        return model

    def predict_smiles(self, smiles: str) -> list[float]:
        """
        Predict Fukui indices for a single SMILES string.

        Args:
            smiles (str): SMILES string of the molecule.

        Returns:
            List[float]: Predicted Fukui indices for each atom.
        """
        # Create a temporary dataset with the single molecule
        df = pd.DataFrame({'smiles': [smiles], 'target': [0.0]})  # dummy target

        dataset = MoleculeDataset(
            df,
            smiles_column='smiles',
            target_column='target',
            addHs=True,
            n_jobs=1,
            skipatom_model=None
        )

        # Create dataloader
        dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)

        predictions = []
        with torch.no_grad():
            for batch in dataloader:
                batch = batch.to(self.device)
                y_hat = self.model(batch.x, batch.edge_index, batch.edge_attr)
                predictions.extend(y_hat.cpu().numpy().tolist())

        return predictions

    def predict_batch(self, smiles_list: list[str]) -> list[list[float]]:
        """
        Predict Fukui indices for a batch of SMILES strings.

        Args:
            smiles_list (List[str]): List of SMILES strings.

        Returns:
            List[List[float]]: List of predicted Fukui indices for each molecule.
        """
        # Create dataset
        df = pd.DataFrame({'smiles': smiles_list, 'target': [0.0] * len(smiles_list)})

        dataset = MoleculeDataset(
            df,
            smiles_column='smiles',
            target_column='target',
            addHs=True,
            n_jobs=1,
            skipatom_model=None
        )

        # Create dataloader
        dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=0)

        all_predictions = []
        with torch.no_grad():
            for batch in dataloader:
                batch = batch.to(self.device)
                y_hat = self.model(batch.x, batch.edge_index, batch.edge_attr)

                # Split predictions by molecule
                start_idx = 0
                for i, _num_atoms in enumerate(batch.ptr[:-1]):
                    end_idx = batch.ptr[i + 1].item()
                    molecule_preds = y_hat[start_idx:end_idx].cpu().numpy().tolist()
                    all_predictions.append(molecule_preds)
                    start_idx = end_idx

        return all_predictions

    def predict_from_csv(self, input_file: str, output_file: str, smiles_column: str = 'smiles'):
        """
        Predict Fukui indices for molecules in a CSV file.

        Args:
            input_file (str): Path to input CSV file.
            output_file (str): Path to output CSV file.
            smiles_column (str): Name of the SMILES column in the input file.
        """
        df = pd.read_csv(input_file)

        if smiles_column not in df.columns:
            raise ValueError(f"Column '{smiles_column}' not found in input file")

        smiles_list = df[smiles_column].tolist()
        predictions = self.predict_batch(smiles_list)

        # Create output DataFrame
        output_data = []
        for _i, (smiles, preds) in enumerate(zip(smiles_list, predictions, strict=False)):
            output_data.append({
                'smiles': smiles,
                'fukui_indices': preds
            })

        output_df = pd.DataFrame(output_data)
        output_df.to_csv(output_file, index=False)
