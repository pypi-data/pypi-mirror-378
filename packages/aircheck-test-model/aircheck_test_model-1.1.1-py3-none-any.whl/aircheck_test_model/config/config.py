from pathlib import Path
import os

# Global variable to store resolved model dir
MODEL_DIR: Path | None = None


def set_model_dir(run_folder_name: Path | str | None = None) -> Path:
    """Set and return the model directory."""
    global MODEL_DIR
    if run_folder_name is None:
        MODEL_DIR = Path.home() / "model"
    else:
        MODEL_DIR = Path(run_folder_name)

    os.makedirs(MODEL_DIR, exist_ok=True)
    return MODEL_DIR


def get_model_dir() -> Path:
    """Get the current model directory (set earlier)."""
    if MODEL_DIR is None:
        # Safety: if CLI forgot to set it, fallback to default
        return set_model_dir()
    return MODEL_DIR


def get_trained_models(model_directory: Path | str | None = None) -> list:
    if model_directory is None:
        main_folder = Path.home() / "model"
    else:
        # main_folder = Path(model_directory)
        main_folder = Path(model_directory).resolve()

    print(f"Looking in: {main_folder}")  # Debug print
    print(f"Directory exists: {main_folder.exists()}")  # Debug print
    model_files = list((main_folder).glob("*/*/model.pkl"))
    model_paths_str = [str(path) for path in model_files]
    return model_paths_str
