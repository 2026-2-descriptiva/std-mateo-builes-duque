import csv
import gzip
from collections import defaultdict


def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        sums = defaultdict(int)
        for row in reader:
            total = sum(int(pair.split(":")[1]) for pair in row[4].split(","))
            sums[row[0]] += total
    return dict(sorted(sums.items()))
