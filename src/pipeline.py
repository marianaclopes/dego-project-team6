import os
import pandas as pd

RAW_PATH = "data/raw/raw_credit_applications.json"
OUTPUT_PATH = "data/clean/credit_applications_clean_v2.parquet"


def load_data(path: str) -> pd.DataFrame:
    """Carica il dataset raw JSON e lo flattena."""
    df = pd.read_json(path)
    df = pd.json_normalize(df.to_dict(orient="records"))
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Applica le regole di pulizia."""
    df = df.copy()  # evita SettingWithCopyWarning

    # Rimuovi duplicati su _id
    if "_id" in df.columns:
        df = df.drop_duplicates(subset=["_id"], keep="first")

    # Converti annual_income in numerico
    if "financials.annual_income" in df.columns:
        df["financials.annual_income"] = pd.to_numeric(
            df["financials.annual_income"], errors="coerce"
        )

    # Credit history negativa -> NA
    if "financials.credit_history_months" in df.columns:
        df.loc[
            df["financials.credit_history_months"] < 0,
            "financials.credit_history_months"
        ] = pd.NA

    # Debt-to-income fuori range [0,1] -> NA
    if "financials.debt_to_income" in df.columns:
        mask = (
            (df["financials.debt_to_income"] < 0) |
            (df["financials.debt_to_income"] > 1)
        )
        df.loc[mask, "financials.debt_to_income"] = pd.NA

    # Rimuovi colonna inutile
    if "processing_timestamp" in df.columns:
        df = df.drop(columns=["processing_timestamp"])

    return df


def save_data(df: pd.DataFrame, path: str) -> None:
    """Salva dataset pulito in parquet."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_parquet(path, index=False)


def main() -> None:
    df_raw = load_data(RAW_PATH)
    df_clean = clean_data(df_raw)
    save_data(df_clean, OUTPUT_PATH)

    print("✅ Pipeline OK")
    print("Output salvato in:", OUTPUT_PATH)
    print("Shape finale:", df_clean.shape)

    if "_id" in df_clean.columns:
        print("Duplicate IDs:", df_clean["_id"].duplicated().sum())


if __name__ == "__main__":
    main()