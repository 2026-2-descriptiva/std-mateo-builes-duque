import csv
import gzip
from collections import defaultdict


def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        groups = defaultdict(list)
        for row in reader:
            groups[row[0]].append(int(row[1]))
    return [(letter, max(vals), min(vals)) for letter, vals in sorted(groups.items())]
