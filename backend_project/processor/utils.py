from pathlib import Path
import os
import pandas as pd

SUPPORTED_EXTS = {".csv", ".xlsx", ".xls"}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_table(fp: Path) -> pd.DataFrame:
    ext = fp.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"Unsupported file format: {ext}. Use .csv/.xlsx/.xls")
    if ext == ".csv":
        return pd.read_csv(fp)
    return pd.read_excel(fp)


def write_excel(df: pd.DataFrame, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(out_path, index=False)
    return out_path


def safe_columns(df, needed):
    for col in needed:
        if col not in df.columns:
            df[col] = None
    return df