import csv
import gzip
from collections import Counter


def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        counts = Counter(
            pair.split(":")[0]
            for row in reader
            for pair in row[4].split(",")
        )
    return dict(sorted(counts.items()))
