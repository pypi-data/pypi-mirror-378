---
license: mit
language:
- en
tags:
- chemistry
- biology
- DFT
- molecular-property-prediction
- graph-neural-networks
- fukui-indices
- reactivity
- pytorch
library_name: transformers
---

# Fukui_Net

Neural network for predicting Fukui indices using Kernel-based Attention Networks (KAN) with Chebyshev graph convolutions.

## Installation

```bash
# Clone and install
git clone https://huggingface.co/Nikolenko-Sergei/FukuiNet
cd FukuiNet
uv sync
```

## Usage

### CLI Interface

The CLI provides a simple interface for molecular analysis:

```bash
# Check available devices and model info
uv run fukui_net info

# Predict single molecule
uv run fukui_net predict "CCO" --device cuda:1

# Batch prediction from CSV file
uv run fukui_net predict --csv molecules.csv --output predictions.csv --device cuda:1
```

**CLI Options:**
- `--device`: Specify device (cpu, cuda:0, cuda:1, etc.)
- `--csv`: Input CSV file with SMILES column
- `--output`: Output CSV file for batch predictions
- `--column`: Name of SMILES column in CSV (default: "smiles")

**Input CSV format:**
```csv
smiles,name
CCO,Ethanol
c1ccccc1,Benzene
```

**Output CSV format:**
```csv
smiles,fukui_indices
CCO,"[-0.322, -0.122, -0.935, ...]"
c1ccccc1,"[-0.280, -0.280, ...]"
```

### Python API

```python
from transformers import AutoModel

# Load model from Hugging Face Hub
model = AutoModel.from_pretrained(
    "Nikolenko-Sergei/FukuiNet",
    trust_remote_code=True
)

# Predict Fukui indices
fukui_indices = model.predict("CCO")
print(f"Fukui indices: {fukui_indices}")

# Batch prediction
results = model.predict_batch(["CCO", "c1ccccc1"])
```

### Direct Usage

```python
from fukui_net.predictor import FukuiNetPredictor

# Load predictor
predictor = FukuiNetPredictor("models/final_model.ckpt", device="cuda:1")

# Predict
fukui_indices = predictor.predict_smiles("CCO")
```

## Model Architecture

- **Graph Neural Network**: Molecular structure as graphs
- **Kernel-based Attention Networks (KAN)**: Advanced attention mechanisms  
- **Chebyshev Convolutions**: Efficient graph operations
- **RDKit Integration**: Molecular featurization

## Input/Output Format

**Input**: SMILES strings (e.g., "CCO", "c1ccccc1")

**Output**: List of Fukui indices for each atom
- Positive values: Electrophilic sites
- Negative values: Nucleophilic sites
- Magnitude: Reactivity strength

## License

MIT License