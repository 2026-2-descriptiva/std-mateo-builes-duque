import re
import pandas as pd


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """
    with open("data/clusters_report.txt", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip 4-line header (titles + separator)
    data_lines = lines[4:]

    rows = []
    current = None

    for line in data_lines:
        line = line.rstrip("\n")

        if not line.strip():
            if current is not None:
                rows.append(current)
                current = None
            continue

        cluster_str = line[0:9].strip()
        kw_text = line[41:].rstrip() if len(line) > 41 else ""

        if cluster_str.isdigit():
            current = {
                "cluster": int(cluster_str),
                "count": int(line[9:25].strip()),
                "pct": float(line[25:41].strip().replace("%", "").replace(",", ".").strip()),
                "kw_parts": [kw_text] if kw_text else [],
            }
        elif current is not None and kw_text:
            current["kw_parts"].append(kw_text)

    if current is not None:
        rows.append(current)

    records = []
    for row in rows:
        kw = re.sub(r"\s+", " ", " ".join(row["kw_parts"])).strip().rstrip(".")
        records.append(
            {
                "cluster": row["cluster"],
                "cantidad_de_palabras_clave": row["count"],
                "porcentaje_de_palabras_clave": row["pct"],
                "principales_palabras_clave": kw,
            }
        )

    return pd.DataFrame(records)
