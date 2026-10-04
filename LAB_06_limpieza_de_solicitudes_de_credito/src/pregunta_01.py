import os
import re
from pathlib import Path

import pandas as pd

SUBMISSION_DIR = Path("submission")
TEXT_COLUMNS = ["sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "línea_credito"]


def _clean_text(series):
    return (
        series.str.lower()
        .str.replace("-", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def _clean_monto(val):
    if pd.isna(val):
        return None
    clean = re.sub(r"[$,\s]", "", str(val))
    return int(float(clean))


def _parse_dates(series):
    dates = pd.to_datetime(series, format="%d/%m/%Y", errors="coerce")
    for fmt in ["%Y-%m-%d", "%Y/%m/%d"]:
        dates = dates.fillna(pd.to_datetime(series, format=fmt, errors="coerce"))
    return dates


def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.
    """
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    df = pd.read_csv(
        "data/solicitudes_de_credito.csv.gz",
        sep=";",
        index_col=0,
        dtype=str,
    )

    # Clean text columns
    for col in TEXT_COLUMNS:
        df[col] = _clean_text(df[col])

    # estrato: int (strip leading zeros)
    df["estrato"] = df["estrato"].str.strip().apply(
        lambda v: int(v) if pd.notna(v) and v != "" else None
    )

    # monto_del_credito: strip $ , . → int
    df["monto_del_credito"] = df["monto_del_credito"].apply(_clean_monto)

    # fecha_de_beneficio: parse then standardize to YYYY-MM-DD
    df["fecha_de_beneficio"] = _parse_dates(df["fecha_de_beneficio"].str.strip()).dt.strftime("%Y-%m-%d")

    # Drop rows with missing values except for comuna_ciudadano
    required_cols = [c for c in df.columns if c != "comuna_ciudadano"]
    df = df.dropna(subset=required_cols)

    # Drop duplicates
    df = df.drop_duplicates()

    # Ensure column order and types
    df["estrato"] = df["estrato"].astype(int)
    df["monto_del_credito"] = df["monto_del_credito"].astype(int)
    df["comuna_ciudadano"] = pd.to_numeric(df["comuna_ciudadano"], errors="coerce")
    df["comuna_ciudadano"] = df["comuna_ciudadano"].where(df["comuna_ciudadano"].notna(), other=None)

    cols = [
        "sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio",
        "estrato", "comuna_ciudadano", "fecha_de_beneficio",
        "monto_del_credito", "línea_credito",
    ]
    df = df[cols].reset_index(drop=True)

    df.to_csv(SUBMISSION_DIR / "solicitudes_de_credito.csv", sep=";", index=False)
