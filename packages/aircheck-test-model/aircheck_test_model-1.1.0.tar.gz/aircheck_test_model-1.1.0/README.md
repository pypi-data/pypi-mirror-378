# AIRCHECK-model

AI models based on AIRCHECK data

## Installation

```bash
pip install AIRCHECK-model
```

## CLI

```bash
aircheck_test_model --help
```

make install

aircheck_test_model train --train-data /path/to/train.csv --column target




# aircheck_test_model

`aircheck_test_model` is a Python package for training and screening machine learning models on chemical compound datasets.  
It provides a command-line interface (CLI) to:

- **Train** models on input datasets  
- **Screen** new compounds using trained models  

The package is designed to work with molecular fingerprints (e.g., ECFP) and chemical structure data in formats such as CSV or Parquet.

---

## Features

- Train ML models with custom training and test datasets  
- Save trained models to a specified directory  
- Evaluate models on test datasets  
- Screen new compounds against trained models  
- Simple CLI powered by [Typer](https://typer.tiangolo.com/)  

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone <your-repo-url>
cd aircheck_test_model
pip install -e '.[dev]'
