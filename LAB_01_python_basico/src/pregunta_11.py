import csv
import gzip
from collections import defaultdict


def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """
    with gzip.open("data/data.csv.gz", "rt") as f:
        reader = csv.reader(f, delimiter="\t")
        sums = defaultdict(int)
        for row in reader:
            val = int(row[1])
            for code in row[3].split(","):
                sums[code] += val
    return dict(sorted(sums.items()))
