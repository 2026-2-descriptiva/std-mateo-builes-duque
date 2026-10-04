import csv
import gzip
from collections import Counter


def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        counts = Counter(row[2][5:7] for row in reader)
    return sorted(counts.items())
