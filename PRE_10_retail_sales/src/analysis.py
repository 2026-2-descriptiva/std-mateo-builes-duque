import os
from pathlib import Path

import pandas as pd

SALES_FILE = "data/sales.csv"
SUBMISSION_DIR = "submission"


def main():
    os.makedirs(SUBMISSION_DIR, exist_ok=True)
    sub = Path(SUBMISSION_DIR)

    sales = pd.read_csv(SALES_FILE)

    sales["OrderDate"] = pd.to_datetime(sales["OrderDate"])
    sales["OrderMonth"] = sales["OrderDate"].dt.to_period("M").dt.to_timestamp()
    sales["DayType"] = sales["OrderDate"].dt.dayofweek.map(
        lambda day: "Fin de semana" if day >= 5 else "Laboral"
    )
    sales["ReturnedAmount"] = sales["TotalAmount"].where(sales["IsReturned"].eq(1), 0)
    sales["NetAmount"] = sales["TotalAmount"] - sales["ReturnedAmount"]

    kpi = pd.DataFrame(
        {
            "orders": [sales["OrderID"].nunique()],
            "customers": [sales["CustomerID"].nunique()],
            "gross_sales": [sales["TotalAmount"].sum()],
            "returned_amount": [sales["ReturnedAmount"].sum()],
            "net_sales": [sales["NetAmount"].sum()],
        }
    )
    kpi["return_rate_by_orders"] = sales["IsReturned"].mean()
    kpi["return_rate_by_value"] = kpi["returned_amount"] / kpi["gross_sales"]
    kpi["net_sales_per_order"] = kpi["net_sales"] / kpi["orders"]
    kpi.to_csv(sub / "kpi_summary.csv", index=False)

    monthly_sales = (
        sales.groupby("OrderMonth")[["TotalAmount", "ReturnedAmount", "NetAmount"]]
        .sum()
        .reset_index()
    )
    monthly_sales = monthly_sales.melt(
        id_vars="OrderMonth", var_name="metric", value_name="amount"
    )
    monthly_sales.to_csv(sub / "monthly_sales.csv", index=False)

    category_summary = (
        sales.groupby("Category")
        .agg(
            orders=("OrderID", "size"),
            gross_sales=("TotalAmount", "sum"),
            returned_amount=("ReturnedAmount", "sum"),
            net_sales=("NetAmount", "sum"),
            return_rate=("IsReturned", "mean"),
        )
        .reset_index()
        .sort_values("net_sales", ascending=False)
    )
    category_summary.to_csv(sub / "category_summary.csv", index=False)

    customer_summary = (
        sales.groupby("CustomerID")
        .agg(
            orders=("OrderID", "size"),
            gross_sales=("TotalAmount", "sum"),
            returned_amount=("ReturnedAmount", "sum"),
            net_sales=("NetAmount", "sum"),
        )
        .reset_index()
    )
    customer_summary["return_rate_by_value"] = (
        customer_summary["returned_amount"] / customer_summary["gross_sales"]
    )
    top_customers = customer_summary.nlargest(10, "net_sales")
    top_customers.to_csv(sub / "top_customers.csv", index=False)

    product_summary = (
        sales.groupby(["Category", "ProductName"])
        .agg(
            orders=("OrderID", "size"),
            net_sales=("NetAmount", "sum"),
            return_rate=("IsReturned", "mean"),
        )
        .reset_index()
    )
    top_products = (
        product_summary.sort_values(["Category", "net_sales"], ascending=[True, False])
        .groupby("Category")
        .head(5)
    )
    top_products.to_csv(sub / "top_products.csv", index=False)

    minimum_orders = 50
    return_risk = (
        sales.groupby(["Category", "SalesChannel"])
        .agg(
            orders=("OrderID", "size"),
            gross_sales=("TotalAmount", "sum"),
            returned_amount=("ReturnedAmount", "sum"),
            return_rate=("IsReturned", "mean"),
        )
        .reset_index()
    )
    return_risk = return_risk[return_risk["orders"] >= minimum_orders].sort_values(
        "return_rate", ascending=False
    )
    return_risk.to_csv(sub / "return_risk.csv", index=False)

    priorities = return_risk.copy()
    priorities["segment"] = priorities["Category"] + " — " + priorities["SalesChannel"]
    priorities = priorities.nlargest(5, "returned_amount")
    priorities.to_csv(sub / "priority_segments.csv", index=False)

    day_type_summary = (
        sales.groupby("DayType")
        .agg(
            orders=("OrderID", "size"),
            gross_sales=("TotalAmount", "sum"),
            net_sales=("NetAmount", "sum"),
            return_rate=("IsReturned", "mean"),
        )
        .reset_index()
    )
    day_type_summary.to_csv(sub / "day_type_summary.csv", index=False)

    payment_summary = (
        sales.groupby("PaymentMethod")
        .agg(
            orders=("OrderID", "size"),
            gross_sales=("TotalAmount", "sum"),
            returned_amount=("ReturnedAmount", "sum"),
            net_sales=("NetAmount", "sum"),
            return_rate=("IsReturned", "mean"),
        )
        .reset_index()
    )
    payment_summary.to_csv(sub / "payment_summary.csv", index=False)


if __name__ == "__main__":
    main()
