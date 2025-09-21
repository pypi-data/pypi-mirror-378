[![stars-badge](https://img.shields.io/github/stars/gao-lab/ExpressionCopilot?logo=GitHub&color=yellow)](https://github.com/gao-lab/ExpressionCopilot/stargazers)
[![build-badge](https://github.com/gao-lab/ExpressionCopilot/actions/workflows/build.yml/badge.svg)](https://github.com/gao-lab/ExpressionCopilot/actions/workflows/build.yml)
[![license-badge](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python>=3.10](https://img.shields.io/badge/python->=3.10-blue.svg)
[![codecov](https://codecov.io/gh/gao-lab/ExpressionCopilot/graph/badge.svg?token=RIoNSWX7J1)](https://codecov.io/gh/gao-lab/ExpressionCopilot)
<!-- ![PyPI](https://img.shields.io/pypi/v/expression_copilot?label=pypi) -->
<!-- [![Downloads](https://static.pepy.tech/badge/expression_copilot)](https://pepy.tech/project/expression_copilot) -->


# Expression Copilot
<div align="center">

[Installation](#Installation) • [Documentation](#Documentation) • [Citation](#Citation) • [FAQ](#FAQ) • [Acknowledgement](#Acknowledgement)

</div>

We introduce two metrics: **EPS** (Expression Predictability Score) and **SPS** (Slice Predictability Score), to quantify the predictability of gene expression from histology image. Python package `expression_copilot` is developed to calculate these metrics efficiently. It also provides several baseline models to predict gene expression from image embeddings, such as MLP.

![expression_copilot](./resource/EPS.png)

## Installation

### PyPI

> [!IMPORTANT]
> Requires Python >= 3.10

We recommend to install `expression_copilot` to a new conda environment:

```sh
mamba create -n expression_copilot -c conda-forge python=3.11 -y && conda activate expression_copilot
pip install expression_copilot
```

(Optional) If you have CUDA-enabled GPU, you could install `cuml`&`cupy` to accelerate KNN building, and install `torch` to accelerate MLP baseline training:
```sh
mamba create -n expression_copilot_cuda -c conda-forge -c rapidsai -c nvidia python=3.11 rapids=25.06 'cuda-version>=12.0,<=12.8' -y && conda activate expression_copilot_cuda
pip install expression_copilot[torch]
```

### Docker
You could pull and use our docker image directly:

```sh
docker pull huhansan666666/expression_copilot:latest

# GPU version
docker run --gpus all -it --rm huhansan666666/expression_copilot:latest

# CPU version
docker run -it --rm huhansan666666/expression_copilot:latest
```

## Documentation

### Quick Start
The following code snippet shows how to calculate EPS and SPS using `expression_copilot`. We assume you have already preprocessed your spatial transcriptomics data into an `AnnData` object (`adata`), where `adata.X` stores raw counts and `adata.obsm['KEY_NAME']` stores image embeddings of spots.

```python
import scanpy as sc
import numpy as np
from expression_copilot import ExpressionCopilotModel

# Read data
# adata.X is expected to be raw counts
# adata.obsm['KEY_NAME'] is expected to store image embeddings of spots
adata = sc.read_h5ad('path/to/adata')

model = ExpressionCopilotModel(adata, image_key = 'KEY_NAME')

# Calculate EPS and SPS
eps = model.calc_metrics_per_gene()
sps = eps.mean()

# Run baseline models (method could be 'ridge', 'linear', 'ensemble', 'mlp')
baseline_metrics_per_gene, _ = model.calc_baseline_metrics(method = 'mlp')
```

### Notebooks
We provide several tutorials in the [resource/tutorials](./resource/tutorials) folder. You could also run them in Google Colab directly:

| Name                                    | Description                                                  | Colab                                                        |
| --------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Basic Tutorial](./resource/tutorials/1-basic_tutorial.ipynb)                | Basic tutorial of calculating EPS                            | [![Open In Colab](https://img.shields.io/badge/Colab-Notebook-blue?logo=googlecolab)](https://colab.research.google.com/drive/1Pa4tdloKcZAa7nqrmURMjS9cdwCzOL9R?usp=sharing) |
| [Advanced Tutorial](./resource/tutorials/2-advanced_tutorial.ipynb)                | Start with 10x spatial-ranger output from scratch                            | [![Open In Colab](https://img.shields.io/badge/Colab-Notebook-blue?logo=googlecolab)](https://colab.research.google.com/drive/1tP3Zg9glSOfNrQT31jaCqdLfqmqNTQup?usp=sharing) |
| [Multi-omics Tutorial](./resource/tutorials/3-multi-omics_tutorial.ipynb)                | Calculating EPS and SPS on single cell multi-omics data                            | [![Open In Colab](https://img.shields.io/badge/Colab-Notebook-blue?logo=googlecolab)](https://colab.research.google.com/drive/1nsfCEQsYGX8u8qtAWIeUXueLTJrzGHc3?usp=sharing) |
## Citation
In coming.

> If you want to repeat results in the manuscript, please check the [**experiments**](./experiments/) folder.

## FAQ
> Please open a new [github issue](https://github.com/gao-lab/ExpressionCopilot/issues/new/choose) if you have any question.

1. `numba` related bugs

We use `numba` to increase the speed (up to 12x). However, it may have compatibility issues with different python/numpy versions. We tested the latest version of numba (0.6.12) and it works fine with Python 3.11/3.12, numpy 1.26.



## Acknowledgement
We thank the following great open-source projects for their help or inspiration:

- [HEST](https://github.com/mahmoodlab/HEST)
- [UNI](https://github.com/mahmoodlab/UNI)
- [entropy_estimators](https://github.com/paulbrodersen/entropy_estimators)
