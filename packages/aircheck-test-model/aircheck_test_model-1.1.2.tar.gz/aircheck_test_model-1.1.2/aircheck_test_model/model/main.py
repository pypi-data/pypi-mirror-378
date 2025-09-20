from pathlib import Path
import json
import os
from typing import Optional
from pyarrow.parquet import ParquetFile
import pyarrow as pa
import pandas as pd

from aircheck_test_model.utils.data_loader import Dataset
from aircheck_test_model.model.test_model import ModelTrainer
from aircheck_test_model.model.eval import ModelEvaluator
from aircheck_test_model.config import config
from aircheck_test_model.model.prediction import screening


def get_model_folder(model_directory: str | None = None) -> Path:
    if model_directory is None:
        # Default: ~/model in the user’s home directory
        run_folder = Path.home() / "model"
    else:
        # Use the provided folder
        run_folder = Path(model_directory)

    # Create the directory if it doesn’t exist
    os.makedirs(run_folder, exist_ok=True)
    return run_folder


def get_trained_models(model_directory: str | None = None) -> Path:
    if model_directory is None:
        main_folder = Path.home() / "model"
    else:
        main_folder = Path(model_directory)
    print("main--folder", main_folder)
    model_files = list((main_folder).glob("*/model.pkl"))
    return model_files


def read_nrows(data_file: str | Path, n_rows: int):
    """Read n rows from given Parquetfile"""
    pf = ParquetFile(data_file)
    rows_to_load = next(pf.iter_batches(batch_size=n_rows))
    first_n_rows = pa.Table.from_batches([rows_to_load]).to_pandas()
    return first_n_rows


if __name__ == "__main__":
    path_name = get_model_folder()
    path_name = get_trained_models()
    print("path name is--", path_name)
    exit()
    dataset = Dataset("ECFP6", "aircheck_test_model/data/WDR91.parquet", "LABEL")
    X = dataset.X
    y = dataset.y
    print(f"type of {type(X)} and y is {type(y)}")


def main(
    train_file: str | Path,
    train_column: str,
    label: str,
    test_file: str | Path | None = None,
    model_dir: str | Path | None = None,
):
    """
    Train models and optionally test them

    Args:
        train_file: Path to training data file (string or Path object)
        train_column: Column name containing the features (e.g ECFP4, EFCP4..)
        label: Column name containing the target labels
        test_file: Optional path to test data file (string or path object)
        model_dir: Optional directory to save/load models (string or path object) if nothing provided model will be saved in user/home/model directory

    Returns:
        Tuple of (train_result_df, test_result_df)

    """
    train_result_df = []
    test_result_df = []
    train_file = Path(train_file)
    if test_file is not None:
        test_file = Path(test_file)
    model_dir = config.set_model_dir(model_dir)
    print("Model Dir------", model_dir)

    if not train_file.exists():
        raise FileNotFoundError(f"Training file not found: {train_file}")
    if test_file and not test_file.exists():
        raise FileNotFoundError(f"Trst file not found: {test_file}")

    try:
        train_df = read_nrows(data_file=train_file, n_rows=10)
        if train_column not in train_df.columns:
            raise ValueError(
                f"Traininf column {train_column} not found in training file. Available columns: {list(train_df.columns)}"
            )
        if label not in train_df.columns:
            raise ValueError(
                f"Traininf column {label} not found in training file. Available columns: {list(train_df.columns)}"
            )

    except Exception as e:
        raise ValueError(f"Error reading training file: {e}")

    if test_file:
        try:
            test_df = read_nrows(data_file=test_file, n_rows=10)
            if train_column not in test_df.columns:
                raise ValueError(
                    f"Training column '{train_column}' not found in test file. Available columns: {list(test_df.columns)}"
                )
            if label not in test_df.columns:
                raise ValueError(
                    f"Label column '{label}' not found in test file. Available columns: {list(test_df.columns)}"
                )
        except Exception as e:
            raise ValueError(f"Error reading test file: {e}")

    # Save training configuration for consistency checking
    if model_dir:
        model_dir = Path(model_dir)

        config_data = {
            "train_column": train_column,
            "label": label,
            "fingerprint_type": train_column,  # Using train_column as fingerprint_type
            "model_directory": str(model_dir),
        }
        print("config data----", config_data)

        config_file = model_dir / "training_config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)
        print(f"Training configuration saved to: {config_file}")
    trainer = ModelTrainer()
    train_result_df = trainer.train_pipeline(
        train_file=train_file, train_column=train_column, label=label, model_dir=model_dir
    )
    print("Finished model training")
    model_eval = ModelEvaluator()
    if test_file:
        print("model starting from here......")
        test_models = config.get_trained_models(model_directory=model_dir)
        print("all models----", test_models)
        test_result_df = model_eval.test_pipeline(
            test_file=test_file, train_column=train_column, label=label, model_path=test_models
        )
    return train_result_df, test_result_df


def screen_compound(
    screen_file: str | Path,
    smile_column: str,
    model_directory: Optional[Path] = None,
    fingerprint_type: Optional[str] = None,
):
    """
    Screen compounds using trained models with automatic consistency validation.

    Args:
        screen_file: Path to file containing compounds to screen (string or Path object)
        smile_column: Column name containing SMILES or molecular data
        model_directory: Directory containing trained models (string or Path object)
        fingerprint_type: Optional fingerprint type (if None, will use training config)

    Returns:
        DataFrame with screening results
    """
    # Convert to Path objects for internal processing
    screen_file = Path(screen_file)
    model_directory = Path(model_directory)

    # Validation
    if not screen_file.exists():
        raise FileNotFoundError(f"Screening file not found: {screen_file}")

    if not model_directory.exists():
        raise FileNotFoundError(f"Model directory not found: {model_directory}")

    # Load and validate training configuration
    config_file = model_directory / "training_config.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                training_config = json.load(f)

            # Use training configuration for consistency
            expected_train_column = training_config.get("train_column")
            expected_fingerprint_type = training_config.get("fingerprint_type")

            # If fingerprint_type not provided, use the one from training
            if fingerprint_type is None:
                fingerprint_type = expected_fingerprint_type
                print(f"Using fingerprint type from training configuration: {fingerprint_type}")

            # Validate consistency
            if fingerprint_type != expected_fingerprint_type:
                raise ValueError(
                    f"Fingerprint type mismatch! Training used '{expected_fingerprint_type}', "
                    f"but screening is trying to use '{fingerprint_type}'. "
                    f"Please use the same fingerprint type as training."
                )

            # Validate that smile_column matches train_column logic
            if smile_column != expected_train_column:
                print(
                    f"Warning: Screening column '{smile_column}' differs from training column '{expected_train_column}'. "
                    f"Make sure they contain compatible data types."
                )

        except json.JSONDecodeError as e:
            raise ValueError(f"Error reading training configuration: {e}")
    else:
        print(
            f"Warning: No training configuration found at {config_file}. "
            f"Cannot validate consistency with training parameters."
        )
        if fingerprint_type is None:
            raise ValueError("fingerprint_type must be provided when no training configuration is available.")

    # Validate screening file columns
    try:
        screen_df = pd.read_csv(screen_file, nrows=1)  # Read just the header
        if smile_column not in screen_df.columns:
            raise ValueError(
                f"SMILES column '{smile_column}' not found in screening file. "
                f"Available columns: {list(screen_df.columns)}"
            )
    except Exception as e:
        raise ValueError(f"Error reading screening file: {e}")

    # Check if models exist in the directory
    model_files = (
        list(model_directory.glob("*.pkl"))
        + list(model_directory.glob("*.joblib"))
        + list(model_directory.glob("*.model"))
    )
    print("********" * 10)
    print("model files----", model_files)
    if not model_directory:
        raise FileNotFoundError(
            f"No model files found in {model_directory}. "
            f"Please ensure models have been trained and saved in this directory."
        )

    print(f"Found {len(model_files)} model files in {model_directory}")
    print(f"Screening compounds using fingerprint type: {fingerprint_type}")

    # Perform screening
    try:
        result_df = screening(screen_file, smile_column, fingerprint_type, model_directory)
        print("Screening completed successfully")
        print("Results preview:")
        print(result_df.head(10))
        return result_df

    except Exception as e:
        raise RuntimeError(f"Error during compound screening: {e}")


# def screening()

# df1,df2 = train(train_file = 'data/WDR91.parquet',train_column='ECFP4',label='LABEL',model_dir = Path('aircheck_test_model/new_model'))

# result_df = screen(screen_file=Path("data/ScreenData1.csv"),smile_column="SMILES",fingerprint_type="ECFP4",model_directory=Path("aircheck_test_model/new_model"))
