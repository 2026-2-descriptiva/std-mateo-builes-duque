import os
from pathlib import Path

import pandas as pd

SUBMISSION_DIR = Path("submission")


def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.

    Ejemplo del formato de cada archivo:

        phrase,target
        "The real estate company posted a net loss ...",negative
        ...
        "Cardona slowed her vehicle , turned around ...",neutral
        ...
    """
    os.makedirs(SUBMISSION_DIR, exist_ok=True)

    for split in sorted(Path("data").iterdir()):
        rows = []
        for target_dir in sorted(split.iterdir()):
            target = target_dir.name
            for txt_file in sorted(target_dir.glob("*.txt")):
                phrase = txt_file.read_text(encoding="utf-8").strip()
                rows.append({"phrase": phrase, "target": target})
        df = pd.DataFrame(rows)
        df.to_csv(SUBMISSION_DIR / f"{split.name}_dataset.csv", index=False)
