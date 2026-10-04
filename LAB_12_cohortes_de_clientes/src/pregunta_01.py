import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SUBMISSION_DIR = Path("submission")


def build_cohort_analysis():
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    df = pd.read_csv("data/sales.csv.gz", parse_dates=["OrderDate"])
    df["order_month"] = df["OrderDate"].dt.to_period("M")

    first = df.groupby("CustomerID")["order_month"].min().rename("cohort")
    df = df.join(first, on="CustomerID")

    df["period_index"] = (df["order_month"] - df["cohort"]).apply(lambda x: x.n)

    cohort_sizes = (
        df[df["period_index"] == 0]
        .groupby("cohort")["CustomerID"]
        .nunique()
        .rename("cohort_size")
    )

    activity = (
        df.groupby(["cohort", "period_index"])["CustomerID"]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )

    activity = activity.join(cohort_sizes, on="cohort")
    activity["cohort_month"] = activity["cohort"].astype(str)
    activity["retention_rate"] = activity["active_customers"] / activity["cohort_size"]

    result = activity[["cohort_month", "period_index", "active_customers", "cohort_size", "retention_rate"]].sort_values(
        ["cohort_month", "period_index"]
    ).reset_index(drop=True)

    result.to_csv(SUBMISSION_DIR / "cohort_retention.csv", index=False)

    # heatmap
    pivot = result.pivot(index="cohort_month", columns="period_index", values="retention_rate")

    fig, ax = plt.subplots(figsize=(max(6, len(pivot.columns) + 1), max(4, len(pivot) + 1)))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlGn", vmin=0, vmax=1)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel("Period Index")
    ax.set_ylabel("Cohort Month")

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if not pd.isna(val):
                ax.text(j, i, f"{val:.0%}", ha="center", va="center", fontsize=8)

    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(SUBMISSION_DIR / "cohort_retention_heatmap.png")
    plt.close()

    return result
