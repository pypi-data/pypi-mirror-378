import os
import pickle
from pathlib import Path

from lightgbm import LGBMClassifier
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import StratifiedKFold
from skopt import BayesSearchCV


import logging
import warnings

from aircheck_test_model.utils.data_loader import Dataset

from aircheck_test_model.utils.model_utils import ConfigLoader
from aircheck_test_model.model.eval_model import ModelEvaluator

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    model_files = list((main_folder).glob("*/model.pkl"))
    return model_files


class ModelTrainer:
    """A utility class for training and evaluating machine learning models."""

    def __init__(self):
        config_dict = ConfigLoader("aircheck_test_model/config/config_loader.yaml")
        self.config_dict = config_dict.config_dict.get("ml-pipeline")

    def get_model(self, model_name: str, best_params: dict | None = None) -> object:
        """Initialize a machine learning model with optional parameters.

        Args:
            model_name: Name of the model to initialize (e.g., 'rf', 'lr', 'svc').
            best_params: Optional dictionary of model parameters. If None, uses default parameters.

        Returns:
            Initialized model instance.

        Raises:
            ValueError: If the model_name is unsupported.
        """
        if not isinstance(model_name, str):
            raise ValueError("model_name must be a string")
        if best_params is not None and not isinstance(best_params, dict):
            raise ValueError("best_params must be a dictionary or None")

        best_params = best_params or {}
        model_name = model_name.lower()

        model_configs = {
            "rf": (RandomForestClassifier, {}),
            "lr": (LogisticRegression, {}),
            "lgbm": (LGBMClassifier, {}),
        }

        if model_name not in model_configs:
            raise ValueError(f"Unsupported model: {model_name}")

        model_class, default_params = model_configs[model_name]
        params = {**default_params, **best_params}
        try:
            return model_class(**params)
        except Exception as e:
            raise ValueError(f"Failed to initialize {model_name} with parameters {params}: {str(e)}")

    def train_model(self, model: object, X_train: np.ndarray, y_train: np.ndarray) -> object:
        """Train a machine learning model on the provided data.

        Args:
            model: Model instance to train.
            X_train: Training feature array.
            y_train: Training label array.

        Returns:
            Trained model instance.

        Raises:
            ValueError: If input arrays are invalid or training fails.
        """
        if not isinstance(X_train, np.ndarray) or not isinstance(y_train, np.ndarray):
            raise ValueError("X_train and y_train must be numpy arrays")
        if X_train.shape[0] != y_train.shape[0]:
            raise ValueError("X_train and y_train must have the same number of samples")
        if X_train.size == 0 or y_train.size == 0:
            raise ValueError("Input arrays cannot be empty")

        try:
            model.fit(X_train, y_train)
            return model
        except Exception as e:
            raise ValueError(f"Failed to train model: {str(e)}")

    # @staticmethod
    def cross_validate_and_save_models(
        self,
        X_train_array: np.ndarray,
        Y_train_array: np.ndarray,
        model_name: str,
        model_subfolder: str | Path,
        Nfold: int,
        best_params: dict | None = None,
    ) -> dict:
        """Perform cross-validation, save fold models, and compute average metrics.

        Args:
            X_train_array: Training feature array.
            Y_train_array: Training label array.
            model_name: Name of the model to train.
            model_subfolder: Folder path to save fold models.
            Nfold: Number of cross-validation folds.
            get_model: Function to initialize a model instance.
            train_model: Function to train a model.
            evaluate_model: Function to evaluate a model.
            best_params: Optional dictionary of model parameters.

        Returns:
            Dictionary of average evaluation metrics across folds.

        Raises:
            ValueError: If inputs are invalid or cross-validation fails.
            FileNotFoundError: If model_subfolder cannot be created.
        """
        if not isinstance(X_train_array, np.ndarray) or not isinstance(Y_train_array, np.ndarray):
            raise ValueError("X_train_array and Y_train_array must be numpy arrays")
        if X_train_array.shape[0] != Y_train_array.shape[0]:
            raise ValueError("X_train_array and Y_train_array must have the same number of samples")
        if not isinstance(Nfold, int) or Nfold < 2:
            raise ValueError("Nfold must be an integer >= 2")
        if not isinstance(model_subfolder, (str, Path)):
            raise ValueError("model_subfolder must be a string or Path")

        model_subfolder = Path(model_subfolder)
        os.makedirs(model_subfolder, exist_ok=True)

        try:
            skf = StratifiedKFold(n_splits=Nfold, shuffle=True, random_state=42)
            fold_metrics = []

            for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X_train_array, Y_train_array)):
                X_train_fold, X_test_fold = X_train_array[train_idx], X_train_array[test_idx]
                y_train_fold, y_test_fold = Y_train_array[train_idx], Y_train_array[test_idx]

                model_fold = self.get_model(model_name, best_params)
                model_fold = self.train_model(model_fold, X_train_fold, y_train_fold)

                fold_model_path = os.path.join(model_subfolder, f"model_fold{fold_idx + 1}")

                fold_model_path = f"{fold_model_path}/model.pkl"
                os.makedirs(os.path.dirname(fold_model_path), exist_ok=True)
                with open(fold_model_path, "wb") as f:
                    pickle.dump(model_fold, f)
                metrics = ModelEvaluator.evaluate_model(model_fold, X_test_fold, y_test_fold)
                print(f"model metrics for fold {fold_idx} is {metrics}")
                metrics["fold_path"] = fold_model_path
                fold_metrics.append(metrics)

            return fold_metrics
        except Exception as e:
            raise ValueError(f"Failed to perform cross-validation: {str(e)}")

    def train_and_save_final_model(
        self,
        config: dict,
        X_train_array: np.ndarray,
        Y_train_array: np.ndarray,
        model_name: str,
        model_subfolder: str | Path,
        best_params: dict | None = None,
    ) -> None:
        """Train a final model and save it to the specified folder.

        Args:
            X_train_array: Training feature array.
            Y_train_array: Training label array.
            model_name: Name of the model to train.
            model_subfolder: Folder path to save the model.
            get_model: Function to initialize a model instance.
            train_model: Function to train a model.
            best_params: Optional dictionary of model parameters.

        Returns:
            None

        Raises:
            ValueError: If inputs are invalid or training fails.
            FileNotFoundError: If model_subfolder cannot be created.
        """
        if not isinstance(X_train_array, np.ndarray) or not isinstance(Y_train_array, np.ndarray):
            raise ValueError("X_train_array and Y_train_array must be numpy arrays")
        if X_train_array.shape[0] != Y_train_array.shape[0]:
            raise ValueError("X_train_array and Y_train_array must have the same number of samples")
        if not isinstance(model_subfolder, (str, Path)):
            raise ValueError("model_subfolder must be a string or Path")

        try:
            model = self.get_model(model_name, best_params)
            model = self.train_model(model, X_train_array, Y_train_array)

        except Exception as e:
            raise ValueError(f"Failed to train and save final model: {str(e)}")

    def bayesian_hyperparameter_search(
        self,
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        cv: int = 5,
        n_iter: int = 32,
        random_state: int = 42,
    ) -> dict:
        """Perform Bayesian hyperparameter optimization for a specified model.

        Args:
            model_name: Name of the model to optimize.
            X_train: Training feature array.
            y_train: Training label array.
            cv: Number of cross-validation folds.
            n_iter: Number of parameter settings to sample.
            random_state: Random seed for reproducibility.

        Returns:
            Dictionary of best hyperparameters.

        Raises:
            ValueError: If inputs are invalid, model is unsupported, or search fails.
        """
        if not isinstance(X_train, np.ndarray) or not isinstance(y_train, np.ndarray):
            raise ValueError("X_train and y_train must be numpy arrays")
        if X_train.shape[0] != y_train.shape[0]:
            raise ValueError("X_train and y_train must have the same number of samples")
        if not isinstance(cv, int) or cv < 2:
            raise ValueError("cv must be an integer >= 2")
        if not isinstance(n_iter, int) or n_iter < 1:
            raise ValueError("n_iter must be a positive integer")

        param_spaces = {
            "rf": {"n_estimators": (100, 200), "max_depth": (5, 15)},
            "lr": {"C": (0.01, 10.0, "log-uniform"), "penalty": ["l2"]},
            "lgbm": {},
            "catboost": {},
        }

        model_name = model_name.lower()
        if model_name not in param_spaces:
            raise ValueError(f"Unsupported model for tuning: {model_name}")
        if not param_spaces[model_name]:
            print(f"Bayesian hyperparameter search is not available for {model_name} in this pipeline.")
            return {}

        try:
            model = self.get_model(model_name)
            search = BayesSearchCV(
                estimator=model, search_spaces=param_spaces[model_name], n_iter=n_iter, cv=cv, random_state=random_state
            )
            search.fit(X_train, y_train)
            return search.best_params_
        except Exception as e:
            raise ValueError(f"Failed to perform hyperparameter search for {model_name}: {str(e)}")

    def train_pipeline(
        self,
        train_file: Path,
        train_column: str,
        label: str,
        model_dir: Path,
    ) -> pd.DataFrame:
        """Execute a training pipeline for multiple models and datasets.

        Args:
            Train: Flag to enable training ('y' or 'n').
            train_paths: List of paths to training parquet files.
            column_names: List of feature column names.
            label_column_train: Name of the label column.
            nrows_train: Number of rows to load from training data, or None for all rows.
            model_names: List of model names to train.
            hyperparameters_tuning: Flag to enable hyperparameter tuning ('y' or 'n').
            RunFolderName: Folder to save models and results.
            feature_fusion_method: Feature fusion method ('all', 'pairwise', or None).
            load_data: Function to load data.
            fuse_columns: Function to fuse columns.
            get_model: Function to initialize a model.
            train_model: Function to train a model.
            cross_validate_and_save_models: Function for cross-validation.
            train_and_save_final_model: Function to train and save final model.
            bayesian_hyperparameter_search: Function for hyperparameter search.
            write_results_csv: Function to write results to CSV.
            hyperparameters: Optional dictionary of model hyperparameters.
            Nfold: Number of cross-validation folds.
            config: Optional configuration dictionary to override parameters.

        Returns:
            None

        Raises:
            ValueError: If inputs are invalid or pipeline execution fails.
            FileNotFoundError: If any training file does not exist.
        """

        if self.config_dict:
            model_names = self.config_dict.get("desired_models")
            hyperparameters_tuning = self.config_dict.get("hyperparameters_tuning", False)
            hyperparameters = self.config_dict.get("hyperparameters")
            Nfold = self.config_dict.get("Nfold")

        model_directory = model_dir

        try:
            for model_name in model_names:
                dataset = Dataset(train_column, train_file, label)
                X_train_array = dataset.X
                Y_train_array = dataset.y
                model_subfolder = model_directory / f"{model_name}_{train_column}"
                os.makedirs(model_subfolder, exist_ok=True)
                best_params = (
                    self.bayesian_hyperparameter_search(model_name, X_train_array, Y_train_array)
                    if hyperparameters_tuning
                    else hyperparameters.get(model_name, {})
                )

                avg_metrics = self.cross_validate_and_save_models(
                    X_train_array=X_train_array,
                    Y_train_array=Y_train_array,
                    model_name=model_name,
                    model_subfolder=model_subfolder,
                    Nfold=Nfold,
                    best_params=best_params,
                )

                self.train_and_save_final_model(
                    self.config_dict, X_train_array, Y_train_array, model_name, model_subfolder, best_params
                )

            df = pd.DataFrame(avg_metrics)
            print(df.head())

        except Exception as e:
            raise ValueError(f"Failed to execute training pipeline: {str(e)}")
        return df


# if __name__ == "__main__":
#     config_dict = ConfigLoader("aircheck_test_model/conf/config_loader.yaml")
#     # print("config dict---", config_dict.config_dict)
#     config_dict = config_dict.config_dict.get("ml-pipeline")
#     # exit()
#     trainer = ModelTrainer()
#     trainer.train_pipeline("aircheck_test_model/conf/model")


def main():
    trainer = ModelTrainer()
    trainer.train_pipeline("aircheck_test_model/conf/model")
