from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_DIR / "data" / "salarios.csv"
SUBMISSION_DIR = PROJECT_DIR / "submission"

PEER_COLS = ["categoria", "trayectoria", "banda_experiencia"]
MIN_GROUP = 30
HIGH_SALARY_QUANTILE = 0.90
GAP_THRESHOLD = -0.05
PROPORTION_THRESHOLD = 0.50


def load_data(path=DATA_FILE):
    df = pd.read_csv(path)
    df["banda_experiencia"] = pd.cut(
        df["experiencia_tecnica_anios"],
        bins=[-1, 4, 9, 14, 100],
        labels=["0-4", "5-9", "10-14", "15+"],
    )
    df["salario_mediano_pares_cop"] = df.groupby(PEER_COLS, observed=True)[
        "salario_mensual_cop"
    ].transform("median")
    df["brecha_vs_pares_pct"] = df["salario_mensual_cop"] / df["salario_mediano_pares_cop"] - 1
    return df


def build_department_gap(df):
    gap = (
        df.groupby(["gerencia", "departamento"], as_index=False)
        .agg(
            profesionales=("employee_id", "size"),
            salario_mediano_cop=("salario_mensual_cop", "median"),
            brecha_mediana_vs_pares_pct=("brecha_vs_pares_pct", "median"),
            proporcion_mas_de_5_pct_debajo=(
                "brecha_vs_pares_pct",
                lambda v: (v <= GAP_THRESHOLD).mean(),
            ),
        )
        .query("profesionales >= @MIN_GROUP")
        .sort_values("brecha_mediana_vs_pares_pct")
        .reset_index(drop=True)
    )
    return gap


def build_recommendations(gap):
    areas = gap.query(
        "brecha_mediana_vs_pares_pct <= @GAP_THRESHOLD and proporcion_mas_de_5_pct_debajo >= @PROPORTION_THRESHOLD"
    ).copy()
    recs = areas.assign(
        alternativa_1="Revisar la banda salarial frente a perfiles comparables.",
        alternativa_2="Verificar criterios de progresión y ajustes salariales.",
        alternativa_3="Priorizar conversación de retención sin divulgar salarios individuales.",
    )[["gerencia", "departamento", "brecha_mediana_vs_pares_pct", "alternativa_1", "alternativa_2", "alternativa_3"]]
    return recs


def build_high_salary(df):
    threshold = df["salario_mensual_cop"].quantile(HIGH_SALARY_QUANTILE)
    df = df.copy()
    df["salario_alto"] = df["salario_mensual_cop"] >= threshold
    summary = df.groupby("trayectoria", as_index=False).agg(
        profesionales=("employee_id", "size"),
        salario_mediano_cop=("salario_mensual_cop", "median"),
        profesionales_con_salario_alto=("salario_alto", "sum"),
        proporcion_con_salario_alto=("salario_alto", "mean"),
    )
    return summary


def build_conclusions(recs, high_salary):
    dept_list = ", ".join(recs["departamento"].tolist())
    tech_high = int(
        high_salary.loc[high_salary["trayectoria"] == "Técnica", "profesionales_con_salario_alto"].iloc[0]
    )
    conclusions = pd.DataFrame([
        {
            "pregunta": "¿Existen áreas con posible brecha salarial interna?",
            "respuesta": f"Sí. Se priorizan {dept_list} para revisar bandas y criterios de progresión.",
            "límite": "La brecha indica una señal para revisión; no identifica su causa por sí sola.",
        },
        {
            "pregunta": "¿La dirección es la única vía hacia salarios altos?",
            "respuesta": f"No. {tech_high} profesionales técnicos están en el decil salarial superior.",
            "límite": "La relación observada no prueba que una trayectoria cause el salario.",
        },
    ])
    return conclusions


def export_tables(output_dir=SUBMISSION_DIR):
    output_dir.mkdir(exist_ok=True)
    df = load_data()
    gap = build_department_gap(df)
    recs = build_recommendations(gap)
    high_salary = build_high_salary(df)
    conclusions = build_conclusions(recs, high_salary)

    gap.to_csv(output_dir / "department_pay_gap.csv", index=False)
    recs.to_csv(output_dir / "compensation_recommendations.csv", index=False)
    high_salary.to_csv(output_dir / "high_salary_by_career.csv", index=False)
    conclusions.to_csv(output_dir / "analysis_conclusions.csv", index=False)


if __name__ == "__main__":
    export_tables()
