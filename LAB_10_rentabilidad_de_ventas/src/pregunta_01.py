import os
from pathlib import Path

import pandas as pd

SUBMISSION_DIR = Path("submission")


def _discount_band(d):
    if d == 0:
        return "0%"
    elif d <= 0.05:
        return "1%-5%"
    elif d <= 0.10:
        return "6%-10%"
    return "más de 10%"


BAND_ORDER = ["0%", "1%-5%", "6%-10%", "más de 10%"]


def _agg(df):
    loss = df[df["Profit"] < 0]
    return pd.Series({
        "lines": len(df),
        "sales": df["Sales"].sum(),
        "profit": df["Profit"].sum(),
        "profit_margin": df["Profit"].sum() / df["Sales"].sum(),
        "loss_line_rate": (df["Profit"] < 0).mean(),
        "lost_profit": (-loss["Profit"]).sum(),
    })


def pregunta_01():
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    df = pd.read_csv("data/superstore_orders.csv.gz", sep=";", decimal=",")

    loss = df[df["Profit"] < 0]

    summary = pd.DataFrame([{
        "lines": len(df),
        "orders": df["Order ID"].nunique(),
        "sales": df["Sales"].sum(),
        "profit": df["Profit"].sum(),
        "profit_margin": df["Profit"].sum() / df["Sales"].sum(),
        "loss_lines": (df["Profit"] < 0).sum(),
        "loss_line_rate": (df["Profit"] < 0).mean(),
        "lost_profit": (-loss["Profit"]).sum(),
    }])
    summary.to_csv(SUBMISSION_DIR / "profitability_summary.csv", index=False)

    df["discount_band"] = df["Discount"].apply(_discount_band)
    discounts = (
        df.groupby("discount_band", sort=False)
        .apply(_agg, include_groups=False)
        .reset_index()
        .set_index("discount_band")
        .loc[BAND_ORDER]
        .reset_index()
    )
    discounts.insert(1, "lines", discounts.pop("lines"))
    discounts.to_csv(SUBMISSION_DIR / "discount_summary.csv", index=False)

    seg_agg = (
        df.groupby(["Customer Segment", "Product Category"], sort=False)
        .apply(_agg, include_groups=False)
        .reset_index()
    )
    seg_agg = seg_agg[seg_agg["lines"] >= 100]
    seg_agg = seg_agg.nlargest(5, "lost_profit")
    seg_agg.insert(2, "lines", seg_agg.pop("lines"))
    segments = seg_agg[["Customer Segment", "Product Category", "lines", "sales", "profit", "profit_margin", "lost_profit"]]
    segments.to_csv(SUBMISSION_DIR / "priority_segments.csv", index=False)

    return summary, discounts, segments
