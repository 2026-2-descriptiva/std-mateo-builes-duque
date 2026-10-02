import os
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
DAY_HOUR_PATH = DATA_DIR / "flights_by_carrier_day_hour.csv.gz"
MONTHLY_PATH = DATA_DIR / "flights_by_carrier_month.csv.gz"
SUBMISSION_DIR = Path("submission")

METRIC_COLUMNS = [
    "scheduled_flights",
    "cancelled_flights",
    "operated_flights",
    "delayed_departure_15_flights",
    "positive_departure_delay_minutes",
]

DAY_NAMES = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado",
    7: "Domingo",
}


def add_rates(frame):
    result = frame.copy()
    result["cancellation_rate"] = result["cancelled_flights"] / result["scheduled_flights"]
    result["delay_rate"] = result["delayed_departure_15_flights"] / result["operated_flights"]
    result["mean_positive_delay_minutes"] = (
        result["positive_departure_delay_minutes"] / result["operated_flights"]
    )
    return result


def main():
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    day_hour = pd.read_csv(DAY_HOUR_PATH)
    monthly = pd.read_csv(MONTHLY_PATH)

    overall = add_rates(monthly[METRIC_COLUMNS].sum().to_frame().T)
    overall.to_csv(SUBMISSION_DIR / "overall_kpis.csv", index=False)

    carrier_summary = add_rates(
        monthly.groupby("reporting_airline")[METRIC_COLUMNS].sum().reset_index()
    ).sort_values("delay_rate", ascending=False)
    top_carriers_by_volume = carrier_summary.nlargest(5, "operated_flights")[
        "reporting_airline"
    ].tolist()
    carrier_summary.to_csv(SUBMISSION_DIR / "carrier_summary.csv", index=False)

    monthly_overall = add_rates(
        monthly.groupby(["year", "month"])[METRIC_COLUMNS].sum().reset_index()
    )
    monthly_overall["period"] = pd.to_datetime(
        dict(year=monthly_overall.year, month=monthly_overall.month, day=1)
    )
    monthly_overall.to_csv(SUBMISSION_DIR / "monthly_national_kpis.csv", index=False)

    calendar_hour = add_rates(
        day_hour.groupby(["day_of_week", "scheduled_departure_hour"])[METRIC_COLUMNS]
        .sum()
        .reset_index()
    )
    calendar_hour.to_csv(SUBMISSION_DIR / "day_hour_delay.csv", index=False)

    minimum_operated_flights = 25_000
    critical = add_rates(
        day_hour.groupby(
            ["reporting_airline", "day_of_week", "scheduled_departure_hour"]
        )[METRIC_COLUMNS]
        .sum()
        .reset_index()
    )
    critical = critical[critical["operated_flights"] >= minimum_operated_flights]
    critical["segment"] = (
        critical["reporting_airline"]
        + " — "
        + critical["day_of_week"].map(DAY_NAMES)
        + " — "
        + critical["scheduled_departure_hour"].map(lambda h: f"{h:02d}:00")
    )
    critical.nlargest(10, "delay_rate").to_csv(
        SUBMISSION_DIR / "priority_segments.csv", index=False
    )

    seasonality = add_rates(
        monthly.groupby(["month", "reporting_airline"])[METRIC_COLUMNS].sum().reset_index()
    )
    seasonality[seasonality["reporting_airline"].isin(top_carriers_by_volume)].to_csv(
        SUBMISSION_DIR / "seasonality.csv", index=False
    )


if __name__ == "__main__":
    main()
