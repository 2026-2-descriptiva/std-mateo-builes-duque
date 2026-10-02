import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

DRIVERS_FILE = "PRE_06_analisis_pandas/data/drivers.csv"
TIMESHEET_FILE = "PRE_06_analisis_pandas/data/timesheet.csv"
SUBMISSION_DIR = "PRE_06_analisis_pandas/submission"
SUMMARY_FILE = f"{SUBMISSION_DIR}/summary.csv"
PLOT_FILE = f"{SUBMISSION_DIR}/top10_drivers.png"


def main():
    drivers = pd.read_csv(DRIVERS_FILE, sep=",", decimal=".")
    timesheet = pd.read_csv(TIMESHEET_FILE, sep=",", decimal=".")

    sum_timesheet = timesheet.groupby("driverId").sum()

    summary = pd.merge(
        sum_timesheet,
        drivers[["driverId", "name"]],
        on="driverId",
    )

    os.makedirs(SUBMISSION_DIR, exist_ok=True)
    summary.to_csv(SUMMARY_FILE, sep=",", header=True, index=False)

    top10 = summary.sort_values(by="miles-logged", ascending=False).head(10)
    top10 = top10.set_index("name")

    top10["miles-logged"].plot.barh(color="tab:orange", alpha=0.6)

    plt.gca().invert_yaxis()
    plt.gca().get_xaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
    )
    plt.xticks(rotation=90)
    plt.gca().spines["left"].set_color("lightgray")
    plt.gca().spines["bottom"].set_color("gray")
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    plt.savefig(PLOT_FILE, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    main()
