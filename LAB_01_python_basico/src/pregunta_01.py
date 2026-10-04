import csv
import gzip


def pregunta_01():
    """
    Calcule la suma de los valores de la segunda columna (`value`) del
    archivo `data/data.csv.gz` y retorne el resultado como un número entero.

    Ejemplo del formato de la respuesta:

        214
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        return sum(int(row[1]) for row in reader)
