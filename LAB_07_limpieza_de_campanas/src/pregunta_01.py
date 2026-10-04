import os
from pathlib import Path

import pandas as pd

SUBMISSION_DIR = Path("submission")


def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Los datos de una campaña de mercadeo bancario llegaron repartidos en diez
    archivos comprimidos. Lee, limpia y separa en tres tablas.
    """
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    parts = [pd.read_csv(f) for f in sorted(Path("data").glob("*.csv.gz"))]
    df = pd.concat(parts, ignore_index=True).drop(columns=["Unnamed: 0"])

    # client table
    client = df[["client_id", "age", "job", "marital", "education", "credit_default", "mortgage"]].copy()
    client["job"] = client["job"].str.replace(".", "", regex=False).str.replace("-", "_", regex=False)
    client["education"] = (
        client["education"]
        .str.replace(".", "_", regex=False)
        .replace("unknown", pd.NA)
    )
    client["credit_default"] = (client["credit_default"] == "yes").astype(int)
    client["mortgage"] = (client["mortgage"] == "yes").astype(int)

    # campaign table
    campaign = df[["client_id", "number_contacts", "contact_duration",
                   "previous_campaign_contacts", "previous_outcome",
                   "campaign_outcome", "month", "day"]].copy()
    campaign["previous_outcome"] = (campaign["previous_outcome"] == "success").astype(int)
    campaign["campaign_outcome"] = (campaign["campaign_outcome"] == "yes").astype(int)
    campaign["last_contact_date"] = pd.to_datetime(
        "2022-" + campaign["month"] + "-" + campaign["day"].astype(str),
        format="%Y-%b-%d",
    ).dt.strftime("%Y-%m-%d")
    campaign = campaign.drop(columns=["month", "day"])

    # economics table
    economics = df[["client_id", "cons_price_idx", "euribor_three_months"]].copy()

    for table, name in [(client, "client.csv"), (campaign, "campaign.csv"), (economics, "economics.csv")]:
        table.to_csv(SUBMISSION_DIR / name, index=False)

    return client, campaign, economics
