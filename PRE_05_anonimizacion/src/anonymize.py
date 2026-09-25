import hashlib
import hmac
import os

import pandas as pd

RAW_FILE = "PRE_05_anonimizacion/data/raw.csv"
OUTPUT_FILE = "PRE_05_anonimizacion/submission/anonymized.csv"

_SECRET_KEY = b"clave-secreta-del-programa"

CITY_TO_DEPARTMENT = {
    "Medellín": "Antioquia",
    "Bello": "Antioquia",
    "Envigado": "Antioquia",
    "Itagüí": "Antioquia",
    "Rionegro": "Antioquia",
    "Bogotá": "Bogotá D.C.",
    "Cali": "Valle del Cauca",
    "Barranquilla": "Atlántico",
    "Manizales": "Caldas",
    "Pereira": "Risaralda",
    "Cartagena": "Bolívar",
    "Bucaramanga": "Santander",
}

DEPARTMENT_TO_REGION = {
    "Antioquia": "Andina",
    "Bogotá D.C.": "Andina",
    "Caldas": "Andina",
    "Risaralda": "Andina",
    "Santander": "Andina",
    "Atlántico": "Caribe",
    "Bolívar": "Caribe",
    "Valle del Cauca": "Pacífica",
}

OCCUPATION_TO_GROUP = {
    "Administradora": "Servicios profesionales",
    "Abogada": "Servicios profesionales",
    "Analista financiera": "Servicios profesionales",
    "Contadora": "Servicios profesionales",
    "Arquitecta": "Tecnología y diseño",
    "Diseñadora gráfica": "Tecnología y diseño",
    "Ingeniero de sistemas": "Tecnología y diseño",
    "Médico": "Salud y educación",
    "Enfermera": "Salud y educación",
    "Docente": "Salud y educación",
    "Comerciante": "Comercio y oficios",
    "Técnico electricista": "Comercio y oficios",
}


def _pseudonymize(document_id):
    digest = hmac.new(
        _SECRET_KEY,
        str(document_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"CUST-{digest[:12].upper()}"


def main():
    df = pd.read_csv(RAW_FILE)

    # Paso 1: eliminar nombre y email
    df = df.drop(columns=["name", "email"])

    # Paso 2: enmascarar loyalty_card_number
    loyalty = df["loyalty_card_number"].astype(str).str.zfill(12)
    df["loyalty_card_number"] = "********" + loyalty.str[-4:]

    # Paso 3: pseudonimizar document_id
    df["customer_id"] = df["document_id"].apply(_pseudonymize)
    df = df.drop(columns=["document_id"])

    # Paso 4: edad en grupos
    df["age_group"] = pd.cut(
        df["age"],
        bins=[20, 30, 40, 50, 60, 70],
        labels=["20-29", "30-39", "40-49", "50-59", "60-69"],
        right=False,
    )
    df = df.drop(columns=["age"])

    # Paso 5: ciudad → departamento → región
    df["department"] = df["city"].map(CITY_TO_DEPARTMENT)
    df["region"] = df["department"].map(DEPARTMENT_TO_REGION)
    df = df.drop(columns=["city", "department"])

    # Paso 6: ocupación → grupo
    df["occupation_group"] = df["occupation"].map(OCCUPATION_TO_GROUP)
    df = df.drop(columns=["occupation"])

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    main()
