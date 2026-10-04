import csv
import gzip
from collections import Counter


def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        counts = Counter(row[0] for row in reader)
    return sorted(counts.items())
