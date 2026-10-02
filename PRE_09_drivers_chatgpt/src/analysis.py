import csv
import os

import matplotlib
import matplotlib.pyplot as plt

DRIVERS_FILE = "data/drivers.csv"
TIMESHEET_FILE = "data/timesheet.csv"
SUBMISSION_DIR = "submission"
SUMMARY_FILE = f"{SUBMISSION_DIR}/summary.csv"
PLOT_FILE = f"{SUBMISSION_DIR}/top10_drivers.png"


def main():
    with open(DRIVERS_FILE, newline="", encoding="utf-8") as f:
        drivers = {row["driverId"]: row["name"] for row in csv.DictReader(f)}

    hours = {}
    miles = {}
    with open(TIMESHEET_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            did = row["driverId"]
            hours[did] = hours.get(did, 0) + int(row["hours-logged"])
            miles[did] = miles.get(did, 0) + int(row["miles-logged"])

    summary = [
        {
            "driver_id": did,
            "hours_logged": hours[did],
            "miles_logged": miles[did],
            "name": drivers[did],
        }
        for did in sorted(drivers, key=lambda x: int(x))
        if did in hours
    ]

    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    with open(SUMMARY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["driver_id", "hours_logged", "miles_logged", "name"])
        writer.writeheader()
        writer.writerows(summary)

    top10 = sorted(summary, key=lambda r: r["miles_logged"], reverse=True)[:10]

    names = [r["name"] for r in top10]
    miles_vals = [r["miles_logged"] for r in top10]

    fig, ax = plt.subplots()
    ax.barh(names, miles_vals, color="tab:orange", alpha=0.6)
    ax.invert_yaxis()
    ax.get_xaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
    )
    plt.xticks(rotation=90)
    ax.spines["left"].set_color("lightgray")
    ax.spines["bottom"].set_color("gray")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.savefig(PLOT_FILE, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    main()
