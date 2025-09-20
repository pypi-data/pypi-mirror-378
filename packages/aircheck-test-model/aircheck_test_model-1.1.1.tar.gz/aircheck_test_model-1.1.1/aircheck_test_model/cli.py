import asyncio
from functools import wraps
from pathlib import Path
import typer

from .settings import settings
from aircheck_test_model.config import config
from aircheck_test_model.model.main import main, screen_compound

app = typer.Typer()


def syncify(f):
    """This simple decorator converts an async function into a sync function,
    allowing it to work with Typer.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@app.command(help=f"Display the current installed version of {settings.project_name}.")
def version():
    from . import __version__

    typer.echo(f"{settings.project_name} - {__version__}")


@app.command(
    "train",
    help=("Run the training pipeline using the static project config, overriding data path and column at runtime."),
)
@syncify
async def train(
    train_file: Path = typer.Option(
        ..., "--train-data", "--t", exists=True, readable=True, help=" Path to the train data file"
    ),
    test_file: Path = typer.Option(None, "--test-data", "--e", help="Path to the test data file"),
    train_column: str = typer.Option(
        ...,
        "--column",
        "-c",
        help="Column name to use (e.g., target/feature depending on your pipeline).",
    ),
    label_column: str = typer.Option(
        ...,
        "--label",
        "-l",
        help="Lable name",
    ),
    model_dir: Path = typer.Option(None, "--model-dir", "-m", help="Directory to save models (default: ~/model)"),
):
    # model_directory = get_model_folder(model_dir)
    model_directory = config.set_model_dir(model_dir)
    main(
        train_file=train_file,
        train_column=train_column,
        label=label_column,
        test_file=test_file,
        model_dir=model_directory,
    )


@app.command(
    "screen",
    help=("Test the compound using trained model."),
)
@syncify
async def screen(
    predict_file: Path = typer.Option(
        ...,
        "--screen-data",
        "--s",
        exists=True,
        readable=True,
        help=" Path to the smile data file",
    ),
    screen_column: str = typer.Option(
        ...,
        "--column",
        "-c",
        help="Column name to use (e.g.,SMILE column name depends on your datafile).",
    ),
    fingerprint_column: str = typer.Option(
        ...,
        "--fingerprints-column",
        "-l",
        help="Fingerprints column name",
    ),
    model_dir: Path = typer.Option(None, "--model-dir", "-m", help="Directory to save models (default: ~/model)"),
):
    # model_directory = get_model_folder(model_dir)
    model_directory = config.set_model_dir(model_dir)
    screen_compound(
        screen_file=predict_file,
        smile_column=screen_column,
        fingerprint_type=fingerprint_column,
        model_directory=model_directory,
    )


if __name__ == "__main__":
    app()


# python -m aircheck_test_model.cli train --train-data data/WDR91.parquet --column  ECFP6 --label  LABEL --model-dir aircheck_test_model/new_model --test-data data/sampled_data_test_1.parquet

# python -m aircheck_test_model.cli screen --screen-data data/ScreenData1.csv --column  SMILES --fingerprints-column  ECFP6 --model-dir aircheck_test_model/new_model

# pip install -e '.[dev]'
# aircheck_test_model train --train-data data/WDR91.parquet --column ECFP6 --label LABEL
