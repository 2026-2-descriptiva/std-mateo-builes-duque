import os
import sqlite3

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

DRIVERS_FILE = "data/drivers.csv"
TIMESHEET_FILE = "data/timesheet.csv"
DB_FILE = "temp/db.sqlite"
SUBMISSION_DIR = "submission"
SUMMARY_FILE = f"{SUBMISSION_DIR}/summary.csv"
PLOT_FILE = f"{SUBMISSION_DIR}/top10_drivers.png"


def main():
    drivers = pd.read_csv(DRIVERS_FILE, sep=",", decimal=".")
    timesheet = pd.read_csv(TIMESHEET_FILE, sep=",", decimal=".")

    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    connection = sqlite3.connect(DB_FILE)

    drivers.to_sql("drivers_raw", connection, if_exists="replace", index=False)
    timesheet.to_sql("timesheet_raw", connection, if_exists="replace", index=False)

    connection.executescript(
        """
        DROP VIEW IF EXISTS drivers;
        DROP VIEW IF EXISTS timesheet;

        CREATE VIEW drivers AS
        SELECT
            driverId AS driver_id,
            name,
            ssn,
            location,
            certified,
            "wage-plan" AS wage_plan
        FROM drivers_raw;

        CREATE VIEW timesheet AS
        SELECT
            driverId AS driver_id,
            week,
            "hours-logged" AS hours_logged,
            "miles-logged" AS miles_logged
        FROM timesheet_raw;
        """
    )
    connection.commit()

    connection.executescript(
        """
        DROP VIEW IF EXISTS driver_summary;

        CREATE VIEW driver_summary AS
        SELECT
            t.driver_id,
            SUM(t.hours_logged) AS hours_logged,
            SUM(t.miles_logged) AS miles_logged,
            d.name
        FROM timesheet AS t
        INNER JOIN drivers AS d
            ON t.driver_id = d.driver_id
        GROUP BY
            t.driver_id,
            d.name;
        """
    )
    connection.commit()

    summary = pd.read_sql_query(
        "SELECT * FROM driver_summary ORDER BY driver_id;", connection
    )
    summary.to_csv(SUMMARY_FILE, sep=",", header=True, index=False)

    top10 = pd.read_sql_query(
        """
        SELECT driver_id, hours_logged, miles_logged, name
        FROM driver_summary
        ORDER BY miles_logged DESC
        LIMIT 10;
        """,
        connection,
    )
    connection.close()

    top10 = top10.set_index("name")
    top10["miles_logged"].plot.barh(color="tab:orange", alpha=0.6)

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
