import csv
import gzip
from collections import defaultdict


def pregunta_07():
    """
    Para cada valor distinto de la segunda columna (`value`), construya la
    lista de letras de la primera columna (`letter`) que aparecen con ese
    valor. Conserve las letras repetidas y el orden en que aparecen en el
    archivo. Retorne una lista de tuplas `(valor, letras)` ordenada por el
    valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["E", "B", "E"]), (2, ["A", "E"]), ...]
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        groups = defaultdict(list)
        for row in reader:
            groups[int(row[1])].append(row[0])
    return sorted(groups.items())
