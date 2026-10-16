from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_DIR / "data" / "campaign_data.csv"
SUBMISSION_DIR = PROJECT_DIR / "submission"


def load_data(path=DATA_FILE):
    df = pd.read_csv(path, parse_dates=["utc_date"])
    return df


def export_tables(output_dir=SUBMISSION_DIR):
    output_dir.mkdir(exist_ok=True)
    df = load_data()

    kpis = pd.DataFrame([{
        "impressions": int(df["impressions"].sum()),
        "paid_clicks": int(df["paid_clicks"].sum()),
        "revenue": df["revenue"].sum(),
        "ad_spend": df["ad_spend"].sum(),
        "gross_profit": df["gross_profit"].sum(),
        "roas": df["revenue"].sum() / df["ad_spend"].sum(),
        "cpc": df["ad_spend"].sum() / df["paid_clicks"].sum(),
    }])
    kpis.to_csv(output_dir / "kpis.csv", index=False)

    daily = (
        df.groupby("utc_date", as_index=False)
        .agg(revenue=("revenue", "sum"), ad_spend=("ad_spend", "sum"), gross_profit=("gross_profit", "sum"))
        .sort_values("utc_date")
    )
    daily.to_csv(output_dir / "daily_summary.csv", index=False)

    source = (
        df.groupby("traffic_source", as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            paid_clicks=("paid_clicks", "sum"),
            revenue=("revenue", "sum"),
            ad_spend=("ad_spend", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values("gross_profit", ascending=False)
    )
    source["roas"] = source["revenue"] / source["ad_spend"]
    source["cpc"] = source["ad_spend"] / source["paid_clicks"]
    source.to_csv(output_dir / "source_summary.csv", index=False)

    campaign = (
        df.groupby("template_name", as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            paid_clicks=("paid_clicks", "sum"),
            revenue=("revenue", "sum"),
            ad_spend=("ad_spend", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values("gross_profit", ascending=False)
    )
    campaign.to_csv(output_dir / "campaign_summary.csv", index=False)


if __name__ == "__main__":
    export_tables()
