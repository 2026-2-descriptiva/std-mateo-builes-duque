import os
from pathlib import Path

import pandas as pd

SUBMISSION_DIR = Path("submission")


def pregunta_01():
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    df = pd.read_csv("data/flights_by_carrier_day_hour.csv.gz")

    hourly = (
        df.groupby("scheduled_departure_hour")[["operated_flights", "delayed_departure_15_flights"]]
        .sum()
        .reset_index()
        .sort_values("scheduled_departure_hour")
    )
    hourly["_rate_exact"] = hourly["delayed_departure_15_flights"] / hourly["operated_flights"]
    hourly["delay_rate"] = hourly["_rate_exact"].round(4)

    # national rate per hour (unrounded for expected computation)
    rate_by_hour = hourly.set_index("scheduled_departure_hour")["_rate_exact"]

    hourly = hourly.drop(columns=["_rate_exact"])
    hourly.to_csv(SUBMISSION_DIR / "hourly_delay_rates.csv", index=False)

    carriers = (
        df.groupby("reporting_airline")[["operated_flights", "delayed_departure_15_flights"]]
        .sum()
        .reset_index()
    )
    carriers = carriers[carriers["operated_flights"] >= 100_000]
    carriers["delay_rate"] = (
        carriers["delayed_departure_15_flights"] / carriers["operated_flights"]
    ).round(4)

    # expected delayed flights per carrier
    hour_flights = df.groupby(["reporting_airline", "scheduled_departure_hour"])["operated_flights"].sum()

    def expected(airline):
        sub = hour_flights.get(airline, pd.Series(dtype=float))
        return (sub * rate_by_hour).sum()

    carriers["expected_delayed_flights"] = carriers["reporting_airline"].apply(expected).round(4)
    carriers["observed_to_expected_ratio"] = (
        carriers["delayed_departure_15_flights"] / carriers["expected_delayed_flights"]
    ).round(4)

    carriers["crude_rank"] = carriers["delay_rate"].rank(ascending=False, method="first").astype(int)
    carriers["adjusted_rank"] = carriers["observed_to_expected_ratio"].rank(ascending=False, method="first").astype(int)

    carriers = carriers.sort_values("adjusted_rank").reset_index(drop=True)

    carriers.to_csv(SUBMISSION_DIR / "carrier_adjusted_delays.csv", index=False)

    return hourly, carriers
