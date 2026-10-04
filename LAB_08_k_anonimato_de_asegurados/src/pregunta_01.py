import json
import os
from pathlib import Path

import pandas as pd

SUBMISSION_DIR = Path("submission")
K = 5


def _age_group(age):
    if age < 30:
        return "18-29"
    elif age < 40:
        return "30-39"
    elif age < 50:
        return "40-49"
    return "50-64"


def _bmi_group(bmi):
    if bmi < 18.5:
        return "bajo peso"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "sobrepeso"
    return "obesidad"


def _children_group(c):
    if c == 0:
        return "0"
    elif c <= 2:
        return "1-2"
    return "3+"


def pregunta_01():
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    df = pd.read_csv("data/insurance.csv.gz")

    df["age_group"] = df["age"].apply(_age_group)
    df["bmi_group"] = df["bmi"].apply(_bmi_group)
    df["children_group"] = df["children"].apply(_children_group)

    orig_qi = ["age", "sex", "bmi", "children", "region"]
    orig_sizes = df.groupby(orig_qi)["age"].transform("size")
    original_k = int(orig_sizes.min())
    original_unique_records = int((orig_sizes == 1).sum())

    schemes = {}
    for scheme_name, qi in [
        ("with_children", ["age_group", "sex", "bmi_group", "children_group", "region"]),
        ("without_children", ["age_group", "sex", "bmi_group", "region"]),
    ]:
        class_sizes = df.groupby(qi)["age"].transform("size")
        eq_classes = int(df.groupby(qi).ngroups)
        k_before = int(class_sizes.min())

        mask_keep = class_sizes >= K
        df_pub = df[mask_keep]
        suppressed = int((~mask_keep).sum())
        published = int(mask_keep.sum())
        pub_classes = int(df_pub.groupby(qi).ngroups)

        diversity = df_pub.groupby(qi)["smoker"].transform("nunique")
        classes_no_div = int((df_pub.groupby(qi)["smoker"].nunique() == 1).sum())
        records_no_div = int((diversity == 1).sum())

        schemes[scheme_name] = {
            "quasi_identifiers": qi,
            "equivalence_classes": eq_classes,
            "k_before_suppression": k_before,
            "suppressed_records": suppressed,
            "published_records": published,
            "published_classes": pub_classes,
            "classes_without_smoker_diversity": classes_no_div,
            "records_without_smoker_diversity": records_no_div,
        }

    selected = (
        "without_children"
        if schemes["without_children"]["suppressed_records"] <= schemes["with_children"]["suppressed_records"]
        else "with_children"
    )

    sel_qi = schemes[selected]["quasi_identifiers"]
    sel_sizes = df.groupby(sel_qi)["age"].transform("size")
    df_pub_sel = df[sel_sizes >= K]

    report = {
        "original_k": original_k,
        "original_unique_records": original_unique_records,
        "schemes": schemes,
        "selected_scheme": selected,
        "mean_charges_original": round(df["charges"].mean(), 4),
        "mean_charges_published": round(df_pub_sel["charges"].mean(), 4),
        "smoker_rate_original": round((df["smoker"] == "yes").mean(), 4),
        "smoker_rate_published": round((df_pub_sel["smoker"] == "yes").mean(), 4),
    }

    (SUBMISSION_DIR / "privacy_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    pub_cols = sel_qi + ["smoker", "charges"]
    df_pub_sel[pub_cols].to_csv(SUBMISSION_DIR / "insurance_published.csv", index=False)

    return report
