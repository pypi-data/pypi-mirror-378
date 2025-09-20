import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union
import logging
from aircheck_test_model.config import config
from aircheck_test_model.utils.fps_conversion import MorganFingerprintExtractor, MWExtractor, CrippenClogPExtractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPredictor:
    def __init__(self, model_path: Union[str, Path]):
        """
        Initialize the predictor with a saved model.

        Args:
            model_path: Path to the pickle file containing the saved model
        """
        self.model_path = Path(model_path)
        self.model = None
        self.load_model()

    def load_model(self) -> None:
        """Load the model from pickle file."""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")

            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)

            logger.info(f"Model loaded successfully from {self.model_path}")
            logger.info(f"Model type: {type(self.model).__name__}")

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def predict(self, X: Union[pd.DataFrame, np.ndarray, list]) -> np.ndarray:
        """
        Make predictions using the loaded model.

        Args:
            X: Input data for prediction

        Returns:
            Predictions as numpy array
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        try:
            # Convert input to appropriate format if needed
            if isinstance(X, list):
                X = np.array(X)
            elif isinstance(X, pd.DataFrame):
                X = X.values

            predictions = self.model.predict(X)
            logger.info(f"Generated {len(predictions)} predictions")

            return predictions

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray, list]) -> np.ndarray:
        """
        Get prediction probabilities (if supported by the model).

        Args:
            X: Input data for prediction

        Returns:
            Prediction probabilities as numpy array
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        if not hasattr(self.model, "predict_proba"):
            raise AttributeError(f"Model {type(self.model).__name__} doesn't support predict_proba")

        try:
            # Convert input to appropriate format if needed
            if isinstance(X, list):
                X = np.array(X)
            elif isinstance(X, pd.DataFrame):
                X = X.values

            probabilities = self.model.predict_proba(X)
            conf = probabilities.std(axis=1).tolist()
            logger.info(f"Generated prediction probabilities for {len(probabilities)} samples")

            return probabilities, conf

        except Exception as e:
            logger.error(f"Probability prediction failed: {str(e)}")
            raise


def screening(screen_file: Path, smile_column: str, fingerprint_type: str, model_directory: Path | str) -> pd.DataFrame:
    """
    Run virtual screening on a list of molecules using trained models.

    This function reads a CSV file containing SMILES strings, computes molecular
    fingerprints, and uses trained models to predict probabilities for each molecule.

    Args:
        screen_file (Path): Path to the CSV file containing molecules.
        smile_column (str): Name of the column containing SMILES strings.
        fingerprint_type (str): Type of fingerprint to use. Must be one of:
            ["ECFP4", "ECFP6", "FCFP4", "FCFP6", "MACCS", "RDK", "AVALON",
             "TOPTOR", "ATOMPAIR", "MW", "ALOGP"].
        model_directory (Path | str): Path to the directory containing trained models.

    Returns:
        pd.DataFrame: A DataFrame with screening results containing:
            - SMILES: Molecule SMILES string.
            - Fingerprint: Type of fingerprint used.
            - Pred_Prob: Predicted probability for the positive class.
            - conf: Model confidence.
            - model_name: Name of the model that generated the prediction.

    Raises:
        ValueError: If `smile_column` is not in the CSV or if `fingerprint_type`
                    is not supported.
    """

    available_fingerprints = [
        "ECFP4",
        "ECFP6",
        "FCFP4",
        "FCFP6",
        "MACCS",
        "RDK",
        "AVALON",
        "TOPTOR",
        "ATOMPAIR",
        "MW",
        "ALOGP",
    ]
    fingerprint_classes = {
        "ECFP4": MorganFingerprintExtractor.ecfp4(binary=True),
        "ECFP6": MorganFingerprintExtractor.ecfp6(binary=True),
        "FCFP4": MorganFingerprintExtractor.fcfp4(binary=True),
        "FCFP6": MorganFingerprintExtractor.fcfp6(binary=True),
        "MACCS": MorganFingerprintExtractor.maccs(),
        "RDK": MorganFingerprintExtractor.rdk(binary=True),
        "AVALON": MorganFingerprintExtractor.avalon(),
        "TOPTOR": MorganFingerprintExtractor.top_tor(),
        "ATOMPAIR": MorganFingerprintExtractor.atom_pair(),
        "MW": MWExtractor(),
        "ALOGP": CrippenClogPExtractor(),
    }

    df = pd.read_csv(screen_file)
    smile_column = smile_column.upper()
    fingerprint_type = fingerprint_type.upper()

    if smile_column not in df.columns:
        raise ValueError(f"Column '{smile_column}' not found in CSV. Available columns: {list(df.columns)}")
    smiles_list = df[smile_column].values.tolist()

    if fingerprint_type not in available_fingerprints:
        raise ValueError(f"Column '{fingerprint_type}' not found in CSV. Available columns: {available_fingerprints}")
    fingerprint_column = [fingerprint_type]
    selected_fingerprints = {k: fingerprint_classes[k] for k in fingerprint_column if k in fingerprint_classes}

    trained_models = config.get_trained_models(model_directory=model_directory)
    all_rows = []
    for model_path in trained_models:
        model = ModelPredictor(model_path)
        for k, v in selected_fingerprints.items():
            fps = v.generate_fps(smiles_list).astype(np.float32)
            y_proba, conf = model.predict_proba(fps)
            for smile, prob, c in list(zip(smiles_list, y_proba[:, 1], conf)):
                print(f"{smile}, {model_path}, {prob}")
                all_rows.append(
                    {
                        "SMILES": smile,
                        "Fingerprint": k,
                        "Pred_Prob": prob,
                        "conf": c,
                        "model_name": model_path.split("/")[-2],
                    }
                )
    df = pd.DataFrame(all_rows)
    df = df.groupby(["SMILES"], as_index=False).mean(numeric_only=True)
    print(df.head(10))
    return df


if __name__ == "__main__":
    screening("data/ScreenData1.csv", "SMILEs", "ECFP4", "aircheck_test_model/new_model")
    exit()
    columns = ["ECFP4", "ECFP6", "FCFP4", "FCFP6", "MACCS", "RDK", "AVALON", "TOPTOR", "ATOMPAIR", "MW", "ALOGP"]
    fingerprint_classes = {
        "ECFP4": MorganFingerprintExtractor.ecfp4(binary=True),
        "ECFP6": MorganFingerprintExtractor.ecfp6(binary=True),
        "FCFP4": MorganFingerprintExtractor.fcfp4(binary=True),
        "FCFP6": MorganFingerprintExtractor.fcfp6(binary=True),
        "MACCS": MorganFingerprintExtractor.maccs(),
        "RDK": MorganFingerprintExtractor.rdk(binary=True),
        "AVALON": MorganFingerprintExtractor.avalon(),
        "TOPTOR": MorganFingerprintExtractor.top_tor(),
        "ATOMPAIR": MorganFingerprintExtractor.atom_pair(),
        "MW": MWExtractor(),
        "ALOGP": CrippenClogPExtractor(),
    }
    df = pd.read_csv("data/ScreenData1.csv")
    lst = df["SMILES"].values.tolist()
    smile_column = "SMILES"
    if smile_column not in df.columns:
        raise ValueError(f"Column '{smile_column}' not found in CSV. Available columns: {list(df.columns)}")
    print("list000", lst)
    # exit()
    # selected_fingerprints = fingerprint_classes.get("EFCP6")
    column = "ECFP6"
    if column not in columns:
        raise ValueError(f"Column '{column}' not found in CSV. Available columns: {columns}")
    column = [column]
    selected_fingerprints = {k: fingerprint_classes[k] for k in column if k in fingerprint_classes}
    print(selected_fingerprints)
    # a = selected_fingerprints.generate_fps("CCO", use_tqdm=True)
    fp_data = {}
    for k, v in selected_fingerprints.items():
        try:
            fp_array = v.generate_fps(lst, use_tqdm=True)
            print("type of array---", fp_array.shape)
            fp_data[k] = ", ".join(map(str, fp_array))
        except Exception as e:
            fp_data[k] = ",".join(["nan"] * v._dimension)
            print(f"Error generating fingerprints for {k}: {e}")
    print("fp data---", (fp_data.keys()))
    print("fp data---", (fp_data["ECFP6"]))
    # exit()

    test_models = config.get_trained_models(model_directory="aircheck_test_model/new_model")

    for model_path in test_models:
        print("Model path-", model_path)
        model = ModelPredictor(model_path=model_path)
        for k, v in selected_fingerprints.items():
            fps = v.generate_fps(lst).astype(np.float32)
            y_proba, conf = model.predict_proba(fps)
            print("Prob--", y_proba)
            print("Probabilities:", y_proba)
            print("Positive class:", y_proba[:, 1])
            a = list(zip(lst, y_proba[:, 1], conf))
            df = pd.DataFrame(a)
            print(df.head())
            print(a)
