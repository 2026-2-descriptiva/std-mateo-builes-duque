"""
Simulacion de MapReduce (estilo Hadoop) para conteo de palabras.
"""

import os
import re
import shutil


def delete_folder(folder):
    """Elimina folder si existe."""
    if os.path.isdir(folder):
        shutil.rmtree(folder)


def initialize_folder(folder):
    """Deja folder vacio y creado."""
    delete_folder(folder)
    os.makedirs(folder, exist_ok=True)


def generate_file_copies(n, data_folder="PRE_02_mapreduce/data", input_folder="PRE_02_mapreduce/temp/input"):
    """Copia n veces cada archivo de data_folder a input_folder."""
    os.makedirs(input_folder, exist_ok=True)
    for fname in os.listdir(data_folder):
        src_path = os.path.join(data_folder, fname)
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
        name, ext = os.path.splitext(fname)
        for i in range(n):
            dst_path = os.path.join(input_folder, f"{name}_{i}{ext}")
            with open(dst_path, "w", encoding="utf-8") as f:
                f.write(content)


def mapper(line):
    """Emite (palabra, 1) por cada palabra en la linea."""
    words = re.findall(r"[a-zA-Z']+", line.lower())
    return [(word, 1) for word in words]


def reducer(key, values):
    """Suma los valores asociados a una llave."""
    return sum(values)


def hadoop(input_folder, output_folder, mapper_fn, reducer_fn):
    """Aplica mapper_fn a cada linea de input_folder, agrupa por llave,
    aplica reducer_fn y escribe el resultado en output_folder/part-00000."""

    os.makedirs(output_folder, exist_ok=True)

    grouped = {}
    for fname in sorted(os.listdir(input_folder)):
        path = os.path.join(input_folder, fname)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                for key, value in mapper_fn(line):
                    grouped.setdefault(key, []).append(value)

    with open(os.path.join(output_folder, "part-00000"), "w", encoding="utf-8") as f:
        for key in sorted(grouped):
            f.write(f"{key}\t{reducer_fn(key, grouped[key])}\n")
