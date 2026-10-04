import os
from pathlib import Path

import numpy as np
import pandas as pd

SUBMISSION_DIR = Path("submission")
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _business_days(in_date, out_date):
    # count Mon-Fri days strictly after in_date, up to and including out_date
    start = (in_date + pd.Timedelta(days=1)).values.astype("datetime64[D]")
    end = (out_date + pd.Timedelta(days=1)).values.astype("datetime64[D]")
    return np.busday_count(start, end)


def pregunta_01():
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    frames = []
    for channel, fname in [("letter", "historical_requests_letter.csv.gz"),
                            ("web", "historical_requests_web.csv.gz")]:
        df = pd.read_csv(f"data/{fname}", parse_dates=["in_date", "out_date"])
        df = df.drop_duplicates()
        df["channel"] = channel
        frames.append(df)

    df = pd.concat(frames, ignore_index=True)

    answered = df["out_date"].notna()
    df_ans = df[answered].copy()
    df_ans["calendar_days"] = (df_ans["out_date"] - df_ans["in_date"]).dt.days
    df_ans["business_days"] = _business_days(df_ans["in_date"], df_ans["out_date"])
    df_ans["on_time"] = df_ans["business_days"] <= 15

    # on_time for all (pending = not on_time)
    df["on_time"] = False
    df.loc[df_ans.index, "on_time"] = df_ans["on_time"]

    # channel_summary
    def ch_agg(g):
        g_ans = df_ans[df_ans["channel"] == g.name]
        return pd.Series({
            "requests": len(g),
            "answered": answered[g.index].sum(),
            "pending": (~answered[g.index]).sum(),
            "median_business_days": g_ans["business_days"].median(),
            "on_time_rate": round(g["on_time"].mean(), 4),
        })

    channels = (
        df.groupby("channel")
        .apply(ch_agg, include_groups=False)
        .reset_index()
        .sort_values("channel")
    )
    channels[["requests", "answered", "pending"]] = channels[["requests", "answered", "pending"]].astype(int)
    channels.to_csv(SUBMISSION_DIR / "channel_summary.csv", index=False)

    # yearly_summary
    df["year"] = df["in_date"].dt.year

    def yr_agg(g):
        return pd.Series({
            "requests": len(g),
            "pending": (~answered[g.index]).sum(),
            "on_time_rate": round(g["on_time"].mean(), 4),
        })

    yearly = (
        df.groupby(["year", "channel"])
        .apply(yr_agg, include_groups=False)
        .reset_index()
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )
    yearly[["requests", "pending"]] = yearly[["requests", "pending"]].astype(int)
    yearly.to_csv(SUBMISSION_DIR / "yearly_summary.csv", index=False)

    # entry_day_summary (both channels combined)
    df_ans_all = df_ans.copy()
    df_ans_all = df_ans_all.set_index("day_name")

    def day_agg(g):
        g_ans = df_ans_all[df_ans_all.index == g.name] if g.name in df_ans_all.index else df_ans_all.iloc[0:0]
        g_ans = df_ans[df_ans["day_name"] == g.name]
        return pd.Series({
            "requests": len(g),
            "median_calendar_days": g_ans["calendar_days"].median(),
            "median_business_days": g_ans["business_days"].median(),
        })

    days = (
        df.groupby("day_name")
        .apply(day_agg, include_groups=False)
        .reset_index()
    )
    days["day_name"] = pd.Categorical(days["day_name"], categories=DAY_ORDER, ordered=True)
    days = days.sort_values("day_name").reset_index(drop=True)
    days["requests"] = days["requests"].astype(int)
    days.to_csv(SUBMISSION_DIR / "entry_day_summary.csv", index=False)

    return channels, yearly, days
