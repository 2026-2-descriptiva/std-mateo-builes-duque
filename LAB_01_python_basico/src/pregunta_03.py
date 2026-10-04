import csv
import gzip
from collections import defaultdict


def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        sums = defaultdict(int)
        for row in reader:
            sums[row[0]] += int(row[1])
    return sorted(sums.items())
