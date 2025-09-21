# PyPI Upload Instructions

## Package Ready for PyPI!

The package has been successfully built and is ready for upload to PyPI.

### Built Files:
- `dist/fukui_net-0.1.0-py3-none-any.whl` (19 KB)
- `dist/fukui_net-0.1.0.tar.gz` (16.6 MB)

### To Upload to PyPI:

1. **Register on PyPI** (if not already):
   - Go to https://pypi.org/account/register/
   - Create an account and verify your email

2. **Get API Token**:
   - Go to https://pypi.org/manage/account/
   - Create a new API token
   - Copy the token (starts with `pypi-`)

3. **Upload to TestPyPI first** (recommended):
   ```bash
   cd /home/nikolenko/work/Projects/Fukui_Net
   uv run twine upload --repository testpypi dist/*
   # Username: __token__
   # Password: your-testpypi-token
   ```

4. **Test installation from TestPyPI**:
   ```bash
   pip install -i https://test.pypi.org/simple/ fukui-net
   ```

5. **Upload to Production PyPI**:
   ```bash
   uv run twine upload dist/*
   # Username: __token__
   # Password: your-pypi-token
   ```

6. **Install from PyPI**:
   ```bash
   pip install fukui-net
   ```

### Package Information:
- **Name**: fukui-net
- **Version**: 0.1.0
- **Description**: A neural network for predicting Fukui indices using Kernel-based Attention Networks (KAN) with Chebyshev graph convolutions
- **License**: MIT
- **Homepage**: https://github.com/SergeiNikolenko/Fukui_Net
- **Hugging Face**: https://huggingface.co/Nikolenko-Sergei/FukuiNet

### Usage After Installation:
```bash
# CLI
fukui_net predict "CCO" --device cpu

# Python
from transformers import AutoModel
model = AutoModel.from_pretrained("Nikolenko-Sergei/FukuiNet", trust_remote_code=True)
result = model.predict("CCO")
```

### Package Contents:
- CLI tool (`fukui_net` command)
- Python API (FukuiNetPredictor class)
- Hugging Face integration (AutoModel support)
- Pre-trained model checkpoint
- Complete test suite

The package is production-ready and includes all necessary dependencies!
