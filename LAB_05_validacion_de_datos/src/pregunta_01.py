import json
import os
import re
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "supplier_id", "supplier", "country", "city", "purchase_date",
    "amount", "discount", "weight", "units", "unit_price", "contact_email",
]
SUBMISSION_DIR = Path("submission")
REPORT_FILE = SUBMISSION_DIR / "data_quality_report.json"


def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.
    """
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    df = pd.read_csv(
        "data/ventas.csv.gz",
        na_values=["N/A", ""],
        keep_default_na=False,
        dtype=str,
    )

    # Normalize column names
    df.columns = [
        col.strip().lstrip("﻿").lower().replace(" ", "_")
        for col in df.columns
    ]

    actual_cols = df.columns.tolist()
    missing_required = sorted(c for c in REQUIRED_COLUMNS if c not in actual_cols)
    unexpected = sorted(c for c in actual_cols if c not in REQUIRED_COLUMNS)

    # Duplicate rows
    duplicate_row_count = int(df.duplicated().sum())

    # Duplicate supplier_id rows (all rows where supplier_id appears more than once)
    supplier_id_counts = df["supplier_id"].value_counts()
    duplicate_supplier_id_row_count = int(
        df["supplier_id"].isin(supplier_id_counts[supplier_id_counts > 1].index).sum()
    )

    # Missing values (NaN = empty or N/A)
    missing_by_col = {col: int(df[col].isna().sum()) for col in REQUIRED_COLUMNS if col in actual_cols}

    # Invalid emails: not matching user@domain.ext
    email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    invalid_email_count = int(
        df["contact_email"].dropna().apply(lambda v: not email_pattern.match(v.strip())).sum()
    )

    # Invalid units: numeric but not positive integer (skip missing)
    def is_invalid_unit(val):
        if pd.isna(val):
            return False
        try:
            n = float(val)
            return not (n > 0 and n == int(n))
        except (ValueError, TypeError):
            return True

    invalid_unit_count = int(df["units"].apply(is_invalid_unit).sum())

    # Country distinct values (as-is, sorted)
    country_values = sorted(df["country"].dropna().unique().tolist())

    report = {
        "row_count": len(df),
        "column_count": len(actual_cols),
        "missing_required_columns": missing_required,
        "unexpected_columns": unexpected,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_by_col,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
