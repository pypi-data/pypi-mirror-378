from aircheck_test_model import train, screen
from pathlib import Path


def main():
    train_result, test_result = train(
        train_file=Path("data/WDR91.parquet"),
        train_column="ECFP6",
        label="LABEL",
        model_dir=Path("aircheck_model/new_model"),
    )
    return train_result, test_result


def screen_file():
    result_df = screen(
        screen_file=Path("data/ScreenData1.csv"),
        smile_column="SMILES",
        fingerprint_type="ECFP6",
        model_directory=Path("aircheck_model/new_model"),
    )
    return result_df


if __name__ == "__main__":
    df1, df2 = main()
    print("Printing---", df1.head())
    # print("Printing---", df2.head())

# pip install dist/aircheck_test_model-0.0.0.dev3+gbec2386a7.d20250919-py3-none-any.whl
